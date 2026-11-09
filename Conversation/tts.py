#!/usr/bin/python3
import numpy as np
import sounddevice as sd
from piper import PiperVoice


# *************** PIPER CONFIGURATION ***************
MODEL_PATH = "piper_voices/de_DE-thorsten-medium.onnx"


# Load voice once
print("Loading Gernan Piper Voice....")

voice =PiperVoice.load(MODEL_PATH)

SAMPLE_RATE=voice.config.sample_rate

print(f"Piper ready. Sample rate:{SAMPLE_RATE} Hz")

def speak_streaming(text: str):
    """
    Synthesize a German sentence and play its audio chunks.

    Piper is loaded once at startup, not for every sentence.
    """

    text = text.strip()

    if not text:
        return

    try:
        # Open an audio stream for this sentence.
        with sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
        ) as output:

            # Piper generates audio chunks as it synthesizes.
            for chunk in voice.synthesize(text):

                audio = np.frombuffer(
                    chunk.audio_int16_bytes,
                    dtype=np.int16,
                )

                if audio.size:
                    output.write(audio)

    except Exception as exc:
        print(f"\n[Piper TTS error] {exc}")

# *************** SIMPLE SPEAK FUNCTION ***************

def speak(text: str):
    """Compatibility wrapper for other files that call speak()."""

    speak_streaming(text)


# *************** OPTIONAL TEST ***************

if __name__ == "__main__":
    print("\nTesting German Piper TTS...")

    speak_streaming(
        "Guten Tag! Willkommen in unserem Café. "
        "Was möchten Sie bestellen?"
    )

    print("TTS test complete.")
