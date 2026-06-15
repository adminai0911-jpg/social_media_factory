import wave
import math
import struct
import os

OUTPUT_DIR = r"C:\Users\drsau\.gemini\antigravity-ide\scratch\Viral_Autopilot_Factory\remotion-studio\public"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_wav(filename, duration, gen_sample_func):
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    
    path = os.path.join(OUTPUT_DIR, filename)
    with wave.open(path, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            value = gen_sample_func(t, num_samples, i)
            # Clip
            value = max(-1.0, min(1.0, value))
            packed_value = struct.pack('<h', int(value * 32767.0))
            wav_file.writeframesraw(packed_value)

# 1. Ding: 1200Hz sine with fast exponential decay
def gen_ding(t, num_samples, i):
    freq = 1200.0
    envelope = math.exp(-10.0 * t)
    return math.sin(2.0 * math.pi * freq * t) * envelope * 0.5

# 2. Riser: Frequency sweeps from 50Hz to 1000Hz over 3 seconds, amplitude swells
def gen_riser(t, num_samples, i):
    duration = 3.0
    progress = t / duration
    freq = 50.0 + (1000.0 - 50.0) * (progress ** 2) # exponential sweep
    envelope = progress ** 2 # swell up
    return math.sin(2.0 * math.pi * freq * t) * envelope * 0.5

# 3. Impact: Low frequency burst with noise
import random
def gen_impact(t, num_samples, i):
    freq = 60.0 * math.exp(-10.0 * t) # quick pitch drop
    envelope = math.exp(-5.0 * t)
    noise = random.uniform(-1.0, 1.0) * 0.2
    return (math.sin(2.0 * math.pi * freq * t) + noise) * envelope * 0.8

print("Generating ding.wav...")
generate_wav("ding.wav", 0.5, gen_ding)
print("Generating riser.wav...")
generate_wav("riser.wav", 3.0, gen_riser)
print("Generating impact.wav...")
generate_wav("impact.wav", 1.5, gen_impact)
print("Done!")
