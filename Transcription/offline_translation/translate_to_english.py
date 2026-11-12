#!/usr/bin/python3
import argostranslate.translate

def translate_to_english(text: str)-> str:
    """Translate German text into English offline"""
    # ignore empty input
    if not text or not text.strip():
        return ""

    # Translate locally using our installed model
    return argostranslate.translate.translate(
        text,
        "de",
        "en"
    )

while True:
    text=input("German>> ").strip()

    # Exit the program
    if text.lower() in ("quit", "exit"):
        print("\nBye")
        break

    try:
        english_text=translate_to_english(text)
        print(f"English: {english_text}")

    except Exception as e:
        print(f"Translation failed: {e}")


"""
offline_translation>python translate_to_english.py
German>> Ich bin Allan
2026-10-09 15:17:15 WARNING: Language de package default expects mwt, which has been added
English: I am Allan
German>> ich komme aus Berlin
English: I am from Berlin
German>> Bruder
English: Brother
German>> Schwester
English: Sister
German>> pferd
English: Horse
German>> miene brudder ist lustig
English: My brother is funny.
German>>
English:
German>> deine katze ist schon
English: Your cat is already
German>> meine hund ist brav
English: My dog is good.
"""
