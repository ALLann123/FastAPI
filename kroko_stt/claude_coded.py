import argparse
import queue
import threading
from pathlib import Path

import numpy as np
import sherpa_onnx
import sounddevice as sd
import soundfile as sf
from huggingface_hub import snapshot_download

REPO_ID = "csukuangfj/sherpa-onnx-streaming-zipformer-de-kroko-2025-08-06"
SAMPLE_RATE = 16000  # model expects 16 kHz mono
CHUNK_SECONDS = 0.1  # how much audio we push to the recognizer at a time


def load_recognizer(num_threads: int = 4) -> sherpa_onnx.OnlineRecognizer:
    """Download (first run only, ~71 MB) and load the model."""
    model = Path(
        snapshot_download(REPO_ID, allow_patterns=["*.onnx", "tokens.txt"])
    )
    return sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=str(model / "tokens.txt"),
        encoder=str(model / "encoder.onnx"),
        decoder=str(model / "decoder.onnx"),
        joiner=str(model / "joiner.onnx"),
        num_threads=num_threads,
        sample_rate=SAMPLE_RATE,
        feature_dim=80,
        decoding_method="greedy_search",
        provider="cpu",
        # We stop on Enter, not on silence, so no automatic endpointing.
        enable_endpoint_detection=False,
    )


def _text(recognizer, stream) -> str:
    # Newer sherpa-onnx returns a str, older versions return an object with .text
    result = recognizer.get_result(stream)
    return (result if isinstance(result, str) else result.text).strip()


def _decode_ready(recognizer, stream) -> None:
    while recognizer.is_ready(stream):
        recognizer.decode_stream(stream)


def listen(recognizer: sherpa_onnx.OnlineRecognizer) -> str:
    """Record from the default mic until the user presses Enter; return text."""
    stream = recognizer.create_stream()
    audio_q: "queue.Queue[np.ndarray]" = queue.Queue()
    stop = threading.Event()

    def on_audio(indata, frames, time_info, status):
        if status:
            print(f"[audio warning: {status}]")
        audio_q.put(indata[:, 0].copy())  # mono float32

    def worker():
        last = ""
        while not stop.is_set() or not audio_q.empty():
            try:
                chunk = audio_q.get(timeout=0.1)
            except queue.Empty:
                continue
            stream.accept_waveform(SAMPLE_RATE, chunk)
            _decode_ready(recognizer, stream)
            text = _text(recognizer, stream)
            if text != last:
                last = text
                # show only the tail so the line never wraps
                print("\r\033[K" + text[-100:], end="", flush=True)

    print("\nListening... (press Enter when done)")
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=int(SAMPLE_RATE * CHUNK_SECONDS),
        callback=on_audio,
    ):
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass

    stop.set()
    t.join()

    # Flush: add a little trailing silence so the last word is emitted.
    stream.accept_waveform(SAMPLE_RATE, np.zeros(int(0.66 * SAMPLE_RATE), dtype=np.float32))
    stream.input_finished()
    _decode_ready(recognizer, stream)
    text = _text(recognizer, stream)
    print("\r\033[K", end="")
    return text


def transcribe_file(recognizer, path: str) -> str:
    audio, sr = sf.read(path, dtype="float32", always_2d=True)
    audio = audio[:, 0]
    if sr != SAMPLE_RATE:
        # simple linear resample, fine for a sanity check
        n = int(len(audio) * SAMPLE_RATE / sr)
        audio = np.interp(np.linspace(0, len(audio) - 1, n), np.arange(len(audio)), audio).astype(np.float32)
    stream = recognizer.create_stream()
    stream.accept_waveform(SAMPLE_RATE, audio)
    stream.accept_waveform(SAMPLE_RATE, np.zeros(int(0.66 * SAMPLE_RATE), dtype=np.float32))
    stream.input_finished()
    _decode_ready(recognizer, stream)
    return _text(recognizer, stream)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wav", help="transcribe a wav file instead of the mic")
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()

    print("Loading model...")
    recognizer = load_recognizer(args.threads)

    if args.wav:
        print(transcribe_file(recognizer, args.wav))
        return

    while True:
        cmd = input("\nPress Enter to start recording (q + Enter to quit): ").strip().lower()
        if cmd == "q":
            break
        text = listen(recognizer)
        print(f"Transcription: {text or '(nothing recognised)'}")


if __name__ == "__main__":
    main()

"""
Listening... (press Enter when done)
Wo ist deine Katze?
Transcription: Wo ist deine Katze?

Press Enter to start recording (q + Enter to quit):

Listening... (press Enter when done)
Deine Frau ist gut.
Transcription: Deine Frau ist gut.

Press Enter to start recording (q + Enter to quit):

Listening... (press Enter when done)
Meine Bruder ist alt.
Transcription: Meine Bruder ist alt.

Press Enter to start recording (q + Enter to quit):

Listening... (press Enter when done)
Denn deine Schwester ist und
Transcription: Denn deine Schwester ist und

Press Enter to start recording (q + Enter to quit):

Listening... (press Enter when done)
Wo ist mein Salat?
Transcription: Wo ist mein Salat?

Press Enter to start recording (q + Enter to quit):

Listening... (press Enter when done)
Dein Hund ist brav.
Transcription: Dein Hund ist brav.

Press Enter to start recording (q + Enter to quit):

Listening... (press Enter when done)
Hast du Pferd?
Transcription: Hast du Pferd?

Press Enter to start recording (q + Enter to quit):

Listening... (press Enter when done)
ist hier. Deine Fährt.
Transcription: ist hier. Deine Fährt.

Press Enter to start recording (q + Enter to quit):

Listening... (press Enter when done)
Sie ist meine Tochter, Lisa.
Transcription: Sie ist meine Tochter, Lisa.

Press Enter to start recording (q + Enter to quit):

Listening... (press Enter when done)
Deine Bruder ist lustig
Transcription: Deine Bruder ist lustig.
"""