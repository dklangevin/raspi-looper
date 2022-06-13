import os
import time
import wave
from math import floor
import matplotlib.animation as anim
import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate as integrate

FRAMES = 1000
FRAME_DIVIDE = 1

wav_frames_list = []
for f in os.listdir('wav'):
    if f.endswith('.wav'):
        wav_frames_list.append(wave.open(f, 'rb').readframes(FRAMES))

def f(i):
    if int(i/100)%2 == 0:
        return 100*np.sin(i/100)*np.cos(i/50)+i%60+i%120
    else:
        return 40*np.sin(i/100)*np.cos(i/1000)

def fourier(li, lf, n, f):
    l = (lf-li)/2 
    # Constant term
    a0=1/l*integrate.quad(lambda x: f(x), li, lf)[0]
    # Cosine coefficents
    A = np.zeros((n))
    # Sine coefficents
    B = np.zeros((n))

    for i in range(1,n+1):
        A[i-1]=1/l*integrate.quad(lambda x: f(x)*np.cos(i*np.pi*x/l), li, lf)[0]
        B[i-1]=1/l* integrate.quad(lambda x: f(x)*np.sin(i*np.pi*x/l), li, lf)[0]

    return [a0/2.0, A, B]
N = 200
a0, an, bn = fourier(1, 1000, N, f)

signals = []
for n in range(1, N+1):
    signal = [an[n-1]*np.cos(n*x*np.pi/500) + bn[n-1]*np.sin(n*x*np.pi/500) for x in range(1000)]
    signals.append(signal)

# signals = [(np.frombuffer(frames, dtype='int16') * 0.2).tolist() for frames in wav_frames_list]

# plt.plot(range(1000), signals[1])
# plt.show()
# exit()

# output = signals[0]
output = [0] * FRAMES
output = [a0] * 1000

# plt.ion()

fig = plt.figure(figsize=(16, 8))
ax = fig.add_subplot(111)

line0, = ax.plot(range(1000), [f(i) for i in range(1000)], 'b-') # Returns a tuple of line objects, thus the comma
line1, = ax.plot(range(1000), output, 'r-') # Returns a tuple of line objects, thus the comma
# line2, = ax.plot(range(FRAMES), output, 'b-') # Returns a tuple of line objects, thus the comma

# lines = [line1, line2]

# plt.xlim([0, FRAMES-1])
plt.xlim([0, 1000])
# plt.ylim([-32768, 32768])  
plt.ylim([-1000, 1000])  

# for signal in signals[1:]:
#     for i in range(FRAMES):
#         output[i] = output[i] + signal[i]
#         line.set_ydata(output)
#         fig.canvas.draw()
#         fig.canvas.flush_events()
#         plt.pause(0.001)

# plt.show(block=True)

def update_intitial(i):
    y = output[:i*3]
    x = range(len(y))
    ax.clear()
    plt.xlim([0, FRAMES-1])
    plt.ylim([-32768, 32768])  
    ax.plot(x, y)

def update(i):
    global output
    fd = FRAME_DIVIDE
    k1 = int((i*fd)%(FRAMES))
    k2 = k1+fd
    signal_i = floor((i*fd)/FRAMES)
    signal = signals[signal_i]
    output[k1:k2] = [a + b for a, b in zip(output[k1:k2], signal[k1:k2])]
    x = range(len(output))
    ax.clear()
    plt.xlim([0, FRAMES-1])
    plt.ylim([-32768, 32768])  
    ax.plot(x, output)

def update(i):
    global output
    fd = FRAME_DIVIDE
    k1 = int((i*fd)%(FRAMES))
    k2 = k1+fd
    signal_i = floor((i*fd)/FRAMES)
    signal = signals[signal_i]
    output[k1:k2] = [a + b for a, b in zip(output[k1:k2], signal[k1:k2])]
    line1.set_ydata(output)

output_signals = []
for i in range(N):
    output = [a + b for a, b in zip(output, signals[i])]
    output_signals.append(output)

def update(i):
    line1.set_ydata(output_signals[i])

a = anim.FuncAnimation(fig, update, frames=N, repeat=False, interval=100)
plt.show()



# line_i = 0
# def update(i):
#     global output
#     global line_i
#     fd = FRAME_DIVIDE
#     k1 = int((i*fd)%(FRAMES))
#     k2 = k1+fd
#     signal_i = floor((i*fd)/FRAMES)
#     signal = signals[signal_i]
#     output[k1:k2] = [a + b for a, b in zip(output[k1:k2], signal[k1:k2])]
#     line1.set_ydata(output[:k2])
#     line1.set_xdata(range(len(output[:k2])))
#     line2.set_ydata(output[k2:])
#     line2.set_xdata(range(k2, len(output)))

# a = anim.FuncAnimation(fig, update, frames=int(len(signals)*(FRAMES/FRAME_DIVIDE)), repeat=False, interval=2)
# plt.show()

# exit()
# for i in range(int(len(signals)*(FRAMES/FRAME_DIVIDE))):
#     fd = FRAME_DIVIDE
#     k1 = int((i*fd)%(FRAMES))
#     k2 = k1+3
#     signal_i = floor((i*fd)/FRAMES)
#     print('k1', k1)
#     print('k2', k2)
#     print('signal_i', signal_i)
    
