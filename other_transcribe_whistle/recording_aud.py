
import sounddevice as sd
from scipy.io.wavfile import write

# Recording settings
SAMPLE_RATE = 16000  # 16 kHz audio
DURATION = 5         # Record for 5 seconds
CHANNELS = 1         # Mono audio
OUTPUT_FILE = "german_test.wav"

print("Get ready to speak German...")
input("Press ENTER to start recording.")

print("Recording... Speak German now!")

# Record audio from the default microphone
audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="int16"
)

# Wait until recording finishes
sd.wait()

# Save the audio as a WAV file
write(OUTPUT_FILE, SAMPLE_RATE, audio)

print(f"Recording saved as {OUTPUT_FILE}")
print("You can now test the recording with Whistle.")
