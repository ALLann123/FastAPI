#!/usr/bin/python3
import os
import speech_recognition as sr
import numpy as np
import sounddevice as sd
import argostranslate.translate
from groq import Groq
from dotenv import load_dotenv
from piper import PiperVoice
from piper.config import SynthesisConfig

# API key for Groq
load_dotenv()
client=Groq(
    api_key=os.environ.get("GROQ_AGAIN")
)

#***************Piper Setup**********************
MODEL_PATH="piper_voices/de_DE-thorsten-medium.onnx"
# LOAD THE voice at startup once
voice=PiperVoice.load(MODEL_PATH)

# setup our voice settings
SPEECH_SPEED=1.20 
NOISE_SCALE=0.667
NOISE_W_SCALE=0.8
VOLUME=2.0

# configure the speech synthesis
syn_config=SynthesisConfig(
    length_scale=SPEECH_SPEED,
    noise_scale=NOISE_SCALE,
    noise_w_scale=NOISE_W_SCALE,
    volume=VOLUME,
)
#*************************************************

# *************** ARGOS TRANSLATE SETUP ***************

print("Loading German-to-English translation model...")

# Get the languages installed on this computer
installed_languages = argostranslate.translate.get_installed_languages()

# Find German and English
german = next(
    (lang for lang in installed_languages if lang.code == "de"),
    None
)

english = next(
    (lang for lang in installed_languages if lang.code == "en"),
    None
)

if german is None or english is None:
    raise RuntimeError(
        "German and English language packages must be installed."
    )

# Prepare the translation object once
translator = german.get_translation(english)

# Warm up the translation model before listening
translator.translate("Hallo")

print("Argos Translate is ready!")

# *****************************************************

# Audio the Groq's Whisper
def listen():
    # create speech recognizer object
    recognizer=sr.Recognizer()

    #open the default microphone
    with sr.Microphone() as source:
        # Notify user recording has started
        print("\nListening....")

        # Listen until the user stops speaking
        # recorded audio is stored in a variable 'audio'
        audio=recognizer.listen(source)

    try:
        # speech_recognition gives us the captured audio as WAV bytes
        # Which we send straight to Groq's transcription endpoint
        wav_bytes=audio.get_wav_data()

        # Send the recorded audio to groqs model
        result=client.audio.transcriptions.create(
            file=("mic_input.wav", wav_bytes),
            model="whisper-large-v3",
            response_format="text",
            language="de",
        )
        text=result.strip()

        # Return in lowercase
        return text.lower()

    except Exception as e:
        print(f"Error during transcribing: {e}")
        # return an empty string
        return ""

# Translate German to ENglish
def translate_to_english(text: str)-> str:
    """Translate German text into English offline"""
    #ignore empty input
    if not text or not text.strip():
        return ""

    # translate locally
    return translator.translate(text)

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
        text=listen().strip().lower()

        # Remove punctuations before checking the command
        command = text.strip(" .,!?:;")

        if command in ('quit', 'exit', 'stop'):
            print("\nBye!!")
            break

        if text:
            print(f"You Said: {text}")

            # translate to english
            to_english=translate_to_english(text)
            print(f"In English>> {to_english}")

            # play it
            print("Talking back now.....")
            speak(text)

    except sr.WaitTimeoutError:
        print("No speech detected. Try again.")

    except KeyboardInterrupt:
        print("\nBye!!")
        break
