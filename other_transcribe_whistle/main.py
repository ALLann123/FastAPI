#!/usr/bin/python3
import needle

result=needle.transcribe(
    "german_test.wav",
    language="de",
    word_timestamps=True
)

print("Transcript:", result['text'])
print("Language", result["language"])
print("First-token latency:", result["ttft_ms"], "ms")

"""
other_transcribe_whistle>python main.py
config.json: 100%|█████████████████████████████████████████████████████████████████████████| 603/603 [00:00<?, ?B/s]
Transcript: Das Hund ist brav.
Language de
First-token latency: 1781.4 ms

"""