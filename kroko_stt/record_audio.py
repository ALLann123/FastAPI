import sounddevice as sd
import soundfile as sf
import numpy as np

# ---------- SETTINGS ----------
SAMPLE_RATE = 16000          # Kroko/Sherpa expects 16 kHz
CHANNELS = 1                 # Mono
OUTPUT_FILE = "german_test.wav"
DURATION = 6.0               # Seconds to record


def record_fixed_duration():
    print(f"Recording {DURATION:.1f}s at {SAMPLE_RATE} Hz (mono)...")
    print("Speak now!")

    # Record as float32 directly
    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
    )
    sd.wait()  # Block until recording finishes

    # Ensure it's 1-D (mono)
    audio = np.squeeze(audio)

    sf.write(OUTPUT_FILE, audio, SAMPLE_RATE, subtype="PCM_16")
    print(f"Saved to {OUTPUT_FILE} ({len(audio)/SAMPLE_RATE:.2f}s)")


if __name__ == "__main__":
    record_fixed_duration()