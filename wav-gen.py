import numpy as np
from scipy.io import wavfile

sampleRate = 44100
frequency = 80
length = 5

t = np.linspace(0, length, sampleRate * length)  #  Produces a 5 second Audio-File
y = np.sin(frequency * 2 * np.pi * t) * 2**15 #  Has frequency of 440Hz
y = y.astype(np.int16)

wavfile.write('sine-80.wav', sampleRate, y)