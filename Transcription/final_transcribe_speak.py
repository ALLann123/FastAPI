#!/usr/bin/python3

import os
import queue
import threading

import speech_recognition as sr
import numpy as np
import sounddevice as sd
import argostranslate.translate

from groq import Groq
from dotenv import load_dotenv
from piper import PiperVoice
from piper.config import SynthesisConfig


# ============================================================
# 1. GROQ API SETUP
# ============================================================

load_dotenv()

api_key = os.environ.get("GROQ_AGAIN")

if not api_key:
    raise RuntimeError(
        "GROQ_AGAIN is missing from your .env file."
    )

client = Groq(api_key=api_key)


# ============================================================
# 2. PIPER TEXT-TO-SPEECH SETUP
# ============================================================

MODEL_PATH = "piper_voices/de_DE-thorsten-medium.onnx"

print("Loading Piper voice...")

# Load the voice once instead of reloading it for every response.
voice = PiperVoice.load(MODEL_PATH)

# Voice configuration.
SPEECH_SPEED = 1.20
NOISE_SCALE = 0.667
NOISE_W_SCALE = 0.8
VOLUME = 1.0

syn_config = SynthesisConfig(
    length_scale=SPEECH_SPEED,
    noise_scale=NOISE_SCALE,
    noise_w_scale=NOISE_W_SCALE,
    volume=VOLUME,
)


# ============================================================
# 3. ARGOS TRANSLATE SETUP
# ============================================================

print("Loading German-to-English translation model...")

installed_languages = (
    argostranslate.translate.get_installed_languages()
)

# Find German and English language packages.
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
        "German and English Argos language packages "
        "must be installed."
    )

# Prepare the translation object once.
translator = german.get_translation(english)

# Warm up the translator.
translator.translate("Hallo")

print("Argos Translate is ready!")


# ============================================================
# 4. MICROPHONE INPUT AND GROQ TRANSCRIPTION
# ============================================================

def listen():
    """Record German speech and transcribe it using Groq."""

    recognizer = sr.Recognizer()

    # Finish recording after a short period of silence.
    recognizer.pause_threshold = 0.5
    recognizer.non_speaking_duration = 0.3

    try:
        with sr.Microphone() as source:
            print("\nListening...")

            # Wait up to 5 seconds for speech to start.
            # Record a maximum of 10 seconds per utterance.
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        print("Transcribing with Groq...")

        # Convert the recording to WAV bytes.
        wav_bytes = audio.get_wav_data()

        # Send the complete recording to Groq.
        result = client.audio.transcriptions.create(
            file=("mic_input.wav", wav_bytes),
            model="whisper-large-v3-turbo",
            response_format="text",
            language="de",
        )

        text = result.strip().lower()

        if not text:
            print("No words recognized.")
            return ""

        return text

    except sr.WaitTimeoutError:
        # IMPORTANT: This catches the timeout from listen().
        # The assistant will return to the main loop.
        print("No speech detected. Listening again...")
        return ""

    except sr.UnknownValueError:
        print("Speech could not be understood.")
        return ""

    except Exception as e:
        print(f"Recording/transcription error: {e}")
        return ""


# ============================================================
# 5. GERMAN-TO-ENGLISH TRANSLATION
# ============================================================

def translate_to_english(text: str) -> str:
    """Translate German text into English offline."""

    if not text or not text.strip():
        return ""

    try:
        return translator.translate(text)

    except Exception as e:
        print(f"Translation error: {e}")
        return ""


# ============================================================
# 6. PIPER STREAMING AUDIO PLAYBACK
# ============================================================

def speak(text: str):
    """
    Synthesize speech in a background thread and play audio
    chunks as they become available.

    This can reduce the delay before playback starts.
    """

    if not text or not text.strip():
        print("No text provided to Piper.")
        return

    audio_queue = queue.Queue(maxsize=20)
    finished = threading.Event()
    synthesis_errors = []

    sample_rate = voice.config.sample_rate

    def generate_audio():
        """Generate Piper audio chunks in the background."""

        try:
            for chunk in voice.synthesize(
                text,
                syn_config=syn_config
            ):
                # Convert Piper's 16-bit PCM bytes to NumPy.
                samples = np.frombuffer(
                    chunk.audio_int16_bytes,
                    dtype=np.int16
                ).copy()

                # Queue audio for playback.
                audio_queue.put(samples)

        except Exception as e:
            synthesis_errors.append(e)

        finally:
            # Signal that synthesis has ended.
            finished.set()

    # Start synthesis without blocking playback setup.
    worker = threading.Thread(
        target=generate_audio,
        daemon=True
    )

    worker.start()

    try:
        # Open the audio output stream.
        with sd.OutputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="int16"
        ) as stream:

            # IMPORTANT: is_set() must be called as a method.
            # Keep playing until synthesis finishes and the
            # queue is empty.
            while (
                not finished.is_set()
                or not audio_queue.empty()
            ):
                try:
                    samples = audio_queue.get(timeout=0.1)

                    # Play the next chunk.
                    stream.write(samples.reshape(-1, 1))

                except queue.Empty:
                    continue

        worker.join()

        if synthesis_errors:
            print(
                f"Piper synthesis error: {synthesis_errors[0]}"
            )

    except Exception as e:
        print(f"Audio playback error: {e}")

        # Stop the synthesis worker if playback fails.
        # This prevents a blocked queue from hanging forever.
        while worker.is_alive():
            try:
                audio_queue.get_nowait()
            except queue.Empty:
                pass

            worker.join(timeout=0.1)


# ============================================================
# 7. MAIN ASSISTANT LOOP
# ============================================================

print("\nAssistant is ready!")
print("Speak German. Say 'quit', 'exit', or 'stop' to quit.")

try:
    while True:

        # --------------------------------------------
        # Step 1: Listen and transcribe.
        # --------------------------------------------

        text = listen().strip().lower()

        # A timeout or failed transcription returns "".
        # Continue listening rather than crashing.
        if not text:
            continue

        # Remove punctuation before checking commands.
        command = text.strip(" .,!?:;")

        # --------------------------------------------
        # Step 2: Exit commands.
        # --------------------------------------------

        if command in ("quit", "exit", "stop"):
            print("\nBye!")
            break

        print(f"\nYou said: {text}")

        # --------------------------------------------
        # Step 3: Translate German into English.
        # --------------------------------------------

        to_english = translate_to_english(text)

        print(f"In English: {to_english}")

        # --------------------------------------------
        # Step 4: Speak the English translation.
        # --------------------------------------------

        if to_english:
            print("Talking back now...")

            # Speak the translated English text.
            speak(text)

        else:
            print("Translation is empty. Nothing to speak.")

except KeyboardInterrupt:
    print("\nAssistant stopped.")

finally:
    print("Voice assistant closed.")
