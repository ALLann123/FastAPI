#!/usr/bin/python3
import os
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
# our API key
client=Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


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

    except sr.WaitTimeoutError:
        print("No speech detected. Try again.")

    except KeyboardInterrupt:
        print("\nBye!!")
        break

"""
Transcription>python whsiper_groq.py

Listening......
You Said: vielen dank.

Listening......
You Said: ...

Listening......
You Said: meine schwester ist lehrerin.

Listening......
You Said: er ist mein sohn.

Listening......
You Said: deine frau ist gut.

Listening......
You Said: nein, zuckerbitter.

Listening......
You Said: wo ist das café?

Listening......
You Said: deine hund ist brav.

Listening......
You Said: meine katze ist schon.

Listening......
You Said: freut mich.

Listening......
You Said: sie ist meine doktor, lisa.

Listening......
You Said: dr.

Listening......
You Said: doktor, doktor

Listening......
You Said: tochter

Listening......
You Said: tochter

Listening......
You Said: sie ist meine tochter.

Listening......
You Said: das restaurant ist billig.

Listening......
You Said: max bist du musiker?

Listening......
You Said: ihr ist deine frau.

Listening......
You Said: deine frau ist gut.

Listening......
You Said: die salat ist gut und frisch.

Listening......

Bye!!
"""