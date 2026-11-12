#!/usr/bin/python3
import os
import speech_recognition as sr
import numpy as np
import sounddevice as sd
from groq import Groq
from dotenv import load_dotenv
from piper import PiperVoice
from piper.config import SynthesisConfig

load_dotenv()
# our API key
client=Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

#**********Piper Setup*******
MODEL_PATH="piper_voices/de_DE-thorsten-medium.onnx"
# load the voice at startup once
voice=PiperVoice.load(MODEL_PATH)

# setup our voice settings
SPEECH_SPEED=1.20  # higher=slower; 1.0 = normal
NOISE_SCALE=0.667 # Voice variation
NOISE_W_SCALE=0.8 # Phoneme duration variation
VOLUME=2.0  # Normaal volume

# Configure the speech synthesis
syn_config=SynthesisConfig(
    length_scale=SPEECH_SPEED,
    noise_scale=NOISE_SCALE,
    noise_w_scale=NOISE_W_SCALE,
    volume=VOLUME,
)
#****************************

# Audio to Groq's whisper model for transcription
def listen():
    # create the speech recognizer object
    recognizer=sr.Recognizer()

    # open the default microphone
    with sr.Microphone() as source:
        # Notify the user recording has started
        print("\nListening......")

        # Listen until the user stops speaking
        # recorded audio is stored in a variable 'audio'
        audio=recognizer.listen(source)

    try:
        # speech_recognition gives us the captured audio as WAV bytes
        # which we send straight to Groq'e transcription endpoint
        wav_bytes=audio.get_wav_data()

        # send the recorded audio to Groqs whisper model
        # it converts the spoken words into text
        result=client.audio.transcriptions.create(
            file=("mic_input.wav", wav_bytes),
            model="whisper-large-v3",
            response_format="text",
            language="de",
        )
        text=result.strip()

        # return the text in lowercase
        return text.lower()

    except Exception as e:
        print(f"Transcription error: {e}")
        # return an empty string
        return ""

# Speak back the text
def speak(text: str):
    """Text to speech and play immediately"""
    audio_chunks=[]
    for chunk in voice.synthesize(text, syn_config=syn_config):
        audio_chunks.append(np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16))

    audio=np.concatenate(audio_chunks)
    sd.play(audio, samplerate=voice.config.sample_rate)
    sd.wait() #block until playback finishes


while True:
    try:
        text = listen().strip().lower()

        # Remove punctuation before checking the command
        command = text.strip(" .,!?:;")

        if command in ("quit", "exit", "stop"):
            print("\nBye!!")
            break

        if text:
            print(f"You Said: {text}")

            # play it
            print("Talking back now....")
            speak(text)

    except sr.WaitTimeoutError:
        print("No speech detected. Try again.")

    except KeyboardInterrupt:
        print("\nBye!!")
        break