#!/usr/bin/python3

import json
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer


# ==============================
# 1. Define model path
# ==============================

#MODEL_PATH = "vosk-model-small-en-us-0.15"
MODEL_PATH="vosk-model-small-de-0.15"

# ==============================
# 2. Load Vosk model
# ==============================

try:
    model = Model(MODEL_PATH)

except Exception:
    print(
        f"Please download the Vosk model and unpack it as '{MODEL_PATH}'."
    )
    sys.exit(1)


# ==============================
# 3. Create recognizer
# ==============================

# Vosk works with 16 kHz audio
SAMPLE_RATE = 16000

recognizer = KaldiRecognizer(model, SAMPLE_RATE)


# ==============================
# 4. Microphone callback
# ==============================

def callback(indata, frames, time, status):

    if status:
        print(status)

    audio_data = bytes(indata)
    # Send microphone audio to Vosk
    if recognizer.AcceptWaveform(audio_data):
        
        # A complete phrase has been recognized
        result = json.loads(recognizer.Result())

        text = result.get("text", "")

        if text:
            print("You:", text)


# ==============================
# 5. Start microphone
# ==============================

print("\n================================")
print(" Vosk Microphone Transcription")
print("================================")
print("Speak into your microphone.")
print("Press Ctrl+C to stop.\n")


try:

    # Open microphone stream
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback
    ):

        # Keep microphone running
        while True:
            sd.sleep(1000)


except KeyboardInterrupt:

    print("\n\nStopping microphone...")

    # Get any remaining recognized speech
    final_result = json.loads(recognizer.FinalResult())

    text = final_result.get("text", "")

    if text:
        print("You:", text)

    print("Done.")


except Exception as e:

    print(f"\nMicrophone error: {e}")
