#!/usr/bin/python3
import needle
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import time

# Audio recording settings
SAMPLE_RATE=16000
CHANNELS=1
OUTPUT_FILE="german_test.wav"

def record_audio():
    """Record microphone audio until the user presses Enter"""
    print("\nPress ENTER to start recording")
    input()

    print("Recording... Speak German")
    print("press ENTER again to stop recording")

    # Store mic audio chunks here
    audio_chunks=[]

    # callback receives audio from the mic
    def audio_callback(indata, frames, time_info, status):
        if status:
            print("Audio status: ", status)

        audio_chunks.append(indata.copy())

    # Start recording from the default microphone
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        callback=audio_callback
    ):
        # wait for the second ENTER press
        input()

    # combine the recorded chunks into one audio array
    if not audio_chunks:
        print("No audio recorded")
        return False

    audio=np.concatenate(audio_chunks, axis=0)

    # save the recording as a wav file
    write(OUTPUT_FILE, SAMPLE_RATE, audio)
    print(f"\nRecording saved: {OUTPUT_FILE}")
    return True

def transcribe_audio():
    """Transcribe the saved audio using whistle"""
    print("\nTranscribing German audio.....")

    start_time=time.perf_counter()

    result=needle.transcribe(
        OUTPUT_FILE,
        language="de",
        word_timestamps=True
    )

    elapsed=time.perf_counter()-start_time

    print("\n--- TRANSCRIPTION RESULT ---")
    print("Transcript:", result["text"])
    print("Language:", result["language"])
    print("First-token latency:", result.get("ttft_ms"), "ms")
    print(f"Total transcription time: {elapsed:.2f} seconds")

if __name__=="__main__":
    try:
        while True:
            if record_audio():
                transcribe_audio()

            print("\nReady for another recording")
            print("CTRL+C to exit")

    except KeyboardInterrupt:
        print("\nExiting....")

"""
--- TRANSCRIPTION RESULT ---
Transcript: Meine Bruder ist lustig.
Language: de
First-token latency: 1182.2 ms
Total transcription time: 7.73 seconds

Ready for another recording
CTRL+C to exit

Press ENTER to start recording

--- TRANSCRIPTION RESULT ---
Transcript: Beine Wust ist gut und du.
Language: de
First-token latency: 2664.6 ms
Total transcription time: 5.59 seconds

Ready for another recording
CTRL+C to exit

Press ENTER to start recording


--- TRANSCRIPTION RESULT ---
Transcript: Das Brot ist frisch.
Language: de
First-token latency: 1522.7 ms
Total transcription time: 3.78 seconds

Ready for another recording
CTRL+C to exit

Press ENTER to start recording
"""