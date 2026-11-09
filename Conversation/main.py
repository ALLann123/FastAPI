#!/usr/bin/env python3
import codecs
import queue
import re
import threading
import requests

from mic import MicListener
from stt import KrokoSTT
from tts import speak_streaming
from translation import translate_to_english, warm_up


# Change this if your FastAPI server has a different IP or port.
API_URL = "http://192.168.1.100:8000/coffee"

# Signal used to tell the consumer that streaming has finished.
END = object()


def stream_llm_sentences(message: str, output_queue: queue.Queue):
    """
    Read the FastAPI response incrementally.

    Complete German sentences are sent to the queue as soon as
    possible, while the LLM continues generating the response.
    """

    buffer = ""
    decoder = codecs.getincrementaldecoder("utf-8")()

    try:
        with requests.get(
            API_URL,
            params={"message": message},
            stream=True,
            timeout=(5, 180),
        ) as response:

            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=128):

                if not chunk:
                    continue

                # Decode safely in case a German character is split
                # across two network chunks.
                text = decoder.decode(chunk)
                buffer += text

                # Find sentence boundaries.
                parts = re.split(
                    r"(?<=[.!?])\s+",
                    buffer
                )

                # The last item might be an incomplete sentence.
                buffer = parts.pop()

                for sentence in parts:
                    sentence = sentence.strip()

                    if sentence:
                        output_queue.put(sentence)

            # Flush any remaining UTF-8 characters.
            buffer += decoder.decode(b"", final=True)

            # Send the final sentence even if it has no punctuation.
            if buffer.strip():
                output_queue.put(buffer.strip())

    except Exception as exc:
        output_queue.put(("ERROR", str(exc)))

    finally:
        output_queue.put(END)


def main():

    # Load/check Argos once, rather than during every translation.
    warm_up()

    print("\nStarting German voice assistant...")

    # Initialize our existing microphone and STT modules.
    mic = MicListener()
    stt = KrokoSTT()

    print("\nAssistant ready.")
    print("Speak German, then press Enter when prompted.")
    print("Say 'Auf Wiedersehen' or 'Beenden' to exit.\n")

    exit_phrases = {
        "auf wiedersehen",
        "beenden",
        "programm beenden",
        "tschüss",
        "tschuss",
        "exit",
        "quit",
    }

    while True:

        try:
            input("\nPress Enter to record your German message...")

            # 1. Capture microphone audio.
            audio, sample_rate = mic.listen()

            # 2. Transcribe German audio with Kroko.
            german_input = stt.transcribe(audio, sample_rate)
            german_input = german_input.strip()

            if not german_input:
                print("No speech recognized. Please try again.")
                continue

            print(f"\nYou (German): {german_input}")

            # 3. Translate the recognized speech for terminal display.
            english_input = translate_to_english(german_input)
            print(f"You (English): {english_input}")

            # Exit check uses the original German transcript.
            if german_input.lower().strip(" .!?") in exit_phrases:
                print("Assistant beendet. Auf Wiedersehen!")
                break

            print("\nAssistant is generating a response...\n")

            # 4. Start receiving the LLM response in the background.
            sentence_queue = queue.Queue()

            producer = threading.Thread(
                target=stream_llm_sentences,
                args=(german_input, sentence_queue),
                daemon=True,
            )

            producer.start()

            # 5. Consume each sentence while the LLM is still streaming.
            while True:

                item = sentence_queue.get()

                if item is END:
                    break

                if (
                    isinstance(item, tuple)
                    and item[0] == "ERROR"
                ):
                    print(f"\n[API error] {item[1]}")
                    continue

                german_sentence = item

                # Display original German sentence.
                print(f"Assistant (German): {german_sentence}")

                # Translate the response for English terminal display.
                english_sentence = translate_to_english(
                    german_sentence
                )
                print(f"Assistant (English): {english_sentence}")

                # 6. Speak the original German sentence.
                # The producer keeps reading LLM chunks in the background.
                speak_streaming(german_sentence)

            producer.join()

        except KeyboardInterrupt:
            print("\nAssistant stopped.")
            break

        except Exception as exc:
            print(f"\n[Error] {exc}")


if __name__ == "__main__":
    main()
