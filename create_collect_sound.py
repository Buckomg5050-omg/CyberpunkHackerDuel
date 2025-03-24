import numpy as np
from scipy.io.wavfile import write

# Parameters
sample_rate = 44100  # Sample rate in Hz
duration = 0.2       # Duration in seconds
frequency = 800      # Frequency in Hz for first tone
frequency2 = 1200    # Frequency in Hz for second tone

# Generate time array
t = np.linspace(0, duration, int(sample_rate * duration), False)

# Generate a simple tone with fading
tone1 = np.sin(2 * np.pi * frequency * t) * 0.3
tone2 = np.sin(2 * np.pi * frequency2 * t) * 0.3

# Fade in and out
fade_samples = int(sample_rate * 0.05)  # 50ms fade
fade_in = np.linspace(0, 1, fade_samples)
fade_out = np.linspace(1, 0, fade_samples)

# Apply fade in to beginning
tone1[:fade_samples] *= fade_in
tone2[:fade_samples] *= fade_in

# Apply fade out to end
tone1[-fade_samples:] *= fade_out
tone2[-fade_samples:] *= fade_out

# Combine tones
tone = tone1 + tone2

# Normalize to 16-bit range
tone = np.int16(tone / np.max(np.abs(tone)) * 32767)

# Write the sound file
write('sounds/collect.wav', sample_rate, tone)

print("Successfully created collect.wav sound effect") 