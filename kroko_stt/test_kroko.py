import time
import soundfile as sf
import numpy as np
import sherpa_onnx

# ---------- SETTINGS ----------
MODEL_DIR = "model"
AUDIO_FILE = "german_test.wav"
NUM_THREADS = 2

print("Loading German Kroko model...")
start_load = time.perf_counter()

recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
    tokens=f"{MODEL_DIR}/tokens.txt",
    encoder=f"{MODEL_DIR}/encoder.onnx",
    decoder=f"{MODEL_DIR}/decoder.onnx",
    joiner=f"{MODEL_DIR}/joiner.onnx",
    num_threads=NUM_THREADS,
    sample_rate=16000,
    feature_dim=80,
    decoding_method="greedy_search",
    provider="cpu",
)

print(f"Model loaded in {time.perf_counter() - start_load:.2f} seconds")

# ---------- LOAD AUDIO ----------
audio, sample_rate = sf.read(AUDIO_FILE, dtype="float32")

if audio.ndim == 2:
    audio = audio.mean(axis=1)

audio_duration = len(audio) / sample_rate

# ---------- TRANSCRIBE ----------
stream = recognizer.create_stream()
stream.accept_waveform(sample_rate, audio)

# Pad with silence so trailing words get decoded
stream.accept_waveform(
    sample_rate,
    np.zeros(int(0.66 * sample_rate), dtype=np.float32),
)
stream.input_finished()

start_inference = time.perf_counter()

while recognizer.is_ready(stream):
    recognizer.decode_streams([stream])

inference_time = time.perf_counter() - start_inference

# ---------- RESULT (handles both old and new API) ----------
result = recognizer.get_result(stream)
text = result.text if hasattr(result, "text") else str(result)

print("\nGerman transcript:")
print(text)

print(f"\nAudio duration: {audio_duration:.2f} seconds")
print(f"Inference time: {inference_time:.3f} seconds")
print(f"Real-time factor: {inference_time / max(audio_duration, 0.001):.3f}")


"""
kroko_stt>python test_kroko.py
Loading German Kroko model...
Model loaded in 14.75 seconds

German transcript:
Aber deine Frau ist alt, guten Tag.

Audio duration: 6.00 seconds
Inference time: 1.108 seconds
Real-time factor: 0.185

"""