# main.py
import sys
import time
from mic import MicListener
from stt import KrokoSTT


def main():
    # ---- 1) Load STT model ONCE, before the loop ----
    stt = KrokoSTT(model_dir="model", num_threads=4)

    mic = MicListener(sample_rate=16000)

    print("\nReady. Press Ctrl+C to quit.")
    try:
        while True:
            # ---- 2) Capture ----
            audio, sr = mic.listen()

            # ---- 3) Transcribe ----
            t0 = time.perf_counter()
            text = stt.transcribe(audio, sr)
            elapsed = time.perf_counter() - t0

            dur = len(audio) / sr
            rtf = elapsed / max(dur, 1e-3)

            print(f"\n🗣  {text.strip() or '(empty)'}")
            print(f"   [{dur:.2f}s audio | {elapsed:.2f}s inference | RTF {rtf:.2f}]")

    except KeyboardInterrupt:
        print("\nBye.")
        sys.exit(0)


if __name__ == "__main__":
    main()

"""

Listening....(speak now)
Got it. Processing....

🗣  Deine Frau ist schon
   [2.30s audio | 0.51s inference | RTF 0.22]

Listening....(speak now)
Got it. Processing....

🗣  Meine Papa ist
   [2.30s audio | 0.48s inference | RTF 0.21]

Listening....(speak now)
Got it. Processing....

🗣  Meine Papa ist gut
   [2.24s audio | 0.44s inference | RTF 0.19]

Listening....(speak now)
Got it. Processing....

🗣  Sie ist meine Tochter, Lisa
   [3.39s audio | 0.70s inference | RTF 0.21]

Listening....(speak now)
Got it. Processing....

🗣  Die Kekse ist licker
   [2.11s audio | 0.51s inference | RTF 0.24]

Listening....(speak now)
Got it. Processing....

🗣  Hallo, Kaffee mit Kekse, nein, sock
   [3.14s audio | 0.48s inference | RTF 0.15]

Listening....(speak now)
Got it. Processing....

🗣  Su
   [1.60s audio | 0.18s inference | RTF 0.11]

Listening....(speak now)
Got it. Processing....

🗣  Su
   [1.60s audio | 0.20s inference | RTF 0.12]

Listening....(speak now)
Got it. Processing....

🗣  (empty)
   [3.20s audio | 0.41s inference | RTF 0.13]

Listening....(speak now)
Got it. Processing....

🗣  (empty)
   [1.92s audio | 0.18s inference | RTF 0.09]

Listening....(speak now)
Got it. Processing....

🗣  (empty)
   [1.86s audio | 0.21s inference | RTF 0.11]

Listening....(speak now)
Got it. Processing....

🗣  (empty)
   [1.73s audio | 0.19s inference | RTF 0.11]

Listening....(speak now)
Got it. Processing....

🗣  Die Salat und Zucker
   [2.37s audio | 0.45s inference | RTF 0.19]

Listening....(speak now)
Got it. Processing....

🗣  (empty)
   [1.79s audio | 0.23s inference | RTF 0.13]

Listening....(speak now)
Got it. Processing....

🗣  die mit Kekse
   [3.07s audio | 0.49s inference | RTF 0.16]

Listening....(speak now)
Got it. Processing....

🗣  Die mit Kekse
   [2.24s audio | 0.52s inference | RTF 0.23]
"""