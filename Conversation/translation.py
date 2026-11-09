#!/usr/bin/python3
import argostranslate.translate

def translate_to_english(text:str)->str:
    """Translate German text into English offline"""
    if not text or not text.strip():
        return ""

    try:
        return argostranslate.translate.translate(
            text,
            "de",
            "en",
        )
    except Exception as e:
        print(f"Translation Error: {e}")
        return "[English translation unavailable]"

def warm_up():
    """Check that Argos can translate before the conversation starts"""
    print("Checking Argos....")

    test_result=translate_to_english("Guten Tag.")

    if test_result=="[English translation unavailable]":
        raise RuntimeError(
            "Argos translation failed. Check that the German and" \
            "Enlish Language packages are installed"
        )

    print("Argos is ready")
    print(f"Translation test: Guten Tag.-> {test_result}")