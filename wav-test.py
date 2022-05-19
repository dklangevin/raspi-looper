from ctypes import sizeof
import wave
import numpy as np
import matplotlib.pyplot as plt
import time

w80 = wave.open('sine-80.wav', 'rb')
w440 = wave.open('sine-440.wav', 'rb')
w880 = wave.open('sine-880.wav', 'rb')
w1760 = wave.open('sine-1760.wav', 'rb')
w7040 = wave.open('sine-7040.wav', 'rb')

FRAMES = 1600

frames80 = w80.readframes(FRAMES)
frames1760 = w1760.readframes(FRAMES)

signal = np.frombuffer(frames80, dtype='int16') * 0.5
signal2 = np.frombuffer(frames1760, dtype='int16') * 0.2
signal3 = signal + signal2

signal = signal.tolist()
signal2 = signal2.tolist()
signal3 = signal3.tolist()

# plt.plot(signal)
# plt.show()

plt.ion()
y = signal
# for i in range(FRAMES):
#     plt.clf()
#     plt.xlim([0, FRAMES-1])
#     plt.ylim([-32768, 32768])
#     x = range(FRAMES)
#     y[:i] = signal3[:i]
#     plt.plot(x, y, color='red')
#     plt.draw()
#     plt.pause(0.000001)

# plt.show(block=True)

fig = plt.figure()
ax = fig.add_subplot(111)
line, = ax.plot(range(FRAMES), y, 'r-') # Returns a tuple of line objects, thus the comma


plt.xlim([0, FRAMES-1])
plt.ylim([-32768, 32768])

for i in range(FRAMES):
    y[:i] = signal3[:i]
    line.set_ydata(y)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.000001)

plt.show(block=True)
