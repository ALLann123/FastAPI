#!/usr/bin/python3
import speech_recognition as sr
import numpy as np

class MicListener:
    """Capture Mic Audio and Converst it to 16kHz mono float32"""
    def __init__(self, sample_rate:int=16000):
        self.sample_rate=sample_rate
        self.recognizer=sr.Recognizer()

        # Tune these if you want faster/slower endpointing
        self.recognizer.pause_threshold = 0.8          # silence before "stop"
        self.recognizer.non_speaking_duration = 0.5    # trailing silence kept
        self.recognizer.dynamic_energy_threshold = True

    def listen(self)-> np.ndarray:
        """Record until the user stops speaking. Returns float32 mono @16kHz"""
        with sr.Microphone(sample_rate=self.sample_rate)as source:
            print("\nListening....(speak now)")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio=self.recognizer.listen(source)
            print("Got it. Processing....")

        # AudioData--> raw PCM16 bytes--> numpy
        raw=np.frombuffer(audio.get_raw_data(), dtype=np.int16)

        # If the mic gave us stereo, average to mono
        if audio.sample_width==2 and len(raw) %2==0:
            #Speech_recognition already downmixes 
            pass

        # int16 -> float32 in [-1, 1]
        samples = raw.astype(np.float32) / 32768.0
        return samples, audio.sample_rate