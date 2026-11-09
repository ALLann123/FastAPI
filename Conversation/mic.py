#!/usr/bin/python3

import threading
import time

import numpy as np
import speech_recognition as sr


class MicListener:
    """Capture microphone audio and return float32 audio with its sample rate.

    Recording ends when EITHER:
      - the user presses Enter, or
      - a long silence follows speech (optional safety net).
    """

    def __init__(self, sample_rate: int = 16000, use_silence_stop: bool = True,
                 silence_seconds: float = 2.5):
        self.sample_rate = sample_rate
        self.use_silence_stop = use_silence_stop
        self.silence_seconds = silence_seconds

        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.calibrated = False

    def listen(self) -> tuple:
        """
        Record until Enter is pressed (or a long silence after speech).

        Returns:
            audio: NumPy float32 mono audio
            sample_rate: Sample rate of the recording
        """
        stop_event = threading.Event()

        # Wait for Enter on a background thread so recording never blocks.
        def wait_for_enter():
            input()
            stop_event.set()

        threading.Thread(target=wait_for_enter, daemon=True).start()

        chunk_size = 1024
        frames = []
        heard_speech = False
        last_voice_time = time.monotonic()

        with sr.Microphone(sample_rate=self.sample_rate,
                           chunk_size=chunk_size) as source:

            if not self.calibrated:
                print("Calibrating microphone. Please remain quiet...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.7)
                self.calibrated = True

            print("Listening... speak now. Press Enter when you're done.")

            while not stop_event.is_set():
                buffer = source.stream.read(chunk_size)
                if not buffer:
                    break
                frames.append(buffer)

                # Optional: stop after a long silence following speech.
                if self.use_silence_stop:
                    energy = np.abs(
                        np.frombuffer(buffer, dtype=np.int16)
                    ).mean()
                    now = time.monotonic()

                    if energy > self.recognizer.energy_threshold:
                        heard_speech = True
                        last_voice_time = now
                    elif heard_speech and now - last_voice_time > self.silence_seconds:
                        print("(Long silence detected, stopping.)")
                        break

        print("Recording complete. Processing...")

        raw = np.frombuffer(b"".join(frames), dtype=np.int16)
        samples = raw.astype(np.float32) / 32768.0

        return samples, self.sample_rate


# Optional standalone microphone test.
if __name__ == "__main__":

    mic = MicListener()

    while True:
        try:
            input("\nPress Enter to start recording...")

            audio, sample_rate = mic.listen()

            print("Audio samples:", len(audio))
            print("Sample rate:", sample_rate)
            print("Duration:", round(len(audio) / sample_rate, 2), "seconds")

        except KeyboardInterrupt:
            print("\nMicrophone test stopped.")
            break