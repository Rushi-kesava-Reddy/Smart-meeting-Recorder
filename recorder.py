import sounddevice as sd
import soundfile as sf
import numpy as np
import os

# Microphone settings
DEVICE = 1
SAMPLE_RATE = 44100
CHANNELS = 1
DURATION = 10

# Create meetings folder
os.makedirs("meetings", exist_ok=True)

print("Using microphone:")
print(sd.query_devices(DEVICE))
print(f"Sample rate: {SAMPLE_RATE} Hz")

print("\nRecording started...")
print("Speak now for 10 seconds...")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="float32",
    device=DEVICE
)

sd.wait()

print("Recording completed.")

# Check audio level
max_level = np.max(np.abs(audio))
average_level = np.mean(np.abs(audio))

print(f"Maximum audio level: {max_level:.6f}")
print(f"Average audio level: {average_level:.6f}")

# Save audio
filename = "meetings/meeting.wav"
sf.write(filename, audio, SAMPLE_RATE)

print(f"Audio saved as {filename}")

if max_level < 0.001:
    print("\nWARNING: Microphone signal is very low.")
else:
    print("\nSUCCESS: Microphone audio detected!")