import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from tkinter import TclError

LOWER_FREQ = 100    # lower frequency limit of your voice sound 
HIGHER_FREQ = 2000  # higher frequency limit of you whistle sound

CHANNELS = 1                
FORMAT = pyaudio.paInt16     
RATE = 44100 * 4
CHUNK = 11025 * 2
MIDDLE_FREQ = (LOWER_FREQ + HIGHER_FREQ) / 2

VOLUME_THR = 0.6
NP_INPUT_MAX_VAR = 7000

move = None
direction = None

# pyaudio class instance
p = pyaudio.PyAudio()

# stream object to get data from microphone
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

x = np.arange(0, 2 * CHUNK, 2) 
xf = np.linspace(0, RATE, CHUNK)
lower_prop = LOWER_FREQ / RATE
higher_prop = HIGHER_FREQ / RATE
l_idx = int(lower_prop * CHUNK)
h_idx = int(higher_prop * CHUNK)

plt.ion()
figure, ax = plt.subplots(figsize=(8, 5))
ver_line_low = ax.axvline(color='black')
ver_line_high = ax.axvline(color='black')
ver_line_low.set_xdata(xf[l_idx])
ver_line_high.set_xdata(xf[h_idx])

line_fft, = ax.semilogx(xf, np.random.rand(CHUNK), '-', lw=2)
hor_line = ax.axhline(color='red')
ver_line = ax.axvline(color='red')

while True:
    
    # binary data
    data = stream.read(CHUNK)  
    
    # convert data to integers, make np array, then offset it by 127
    data_int = struct.unpack(str(2 * CHUNK) + 'B', data)
    data_np = np.array(data_int, dtype='b')[::2] + 128
    relative_power = data_np.var()/NP_INPUT_MAX_VAR
    
    # compute FFT and update line
    yf = fft(data_int)
    yf_abs = np.abs(yf[0:CHUNK])  / (128 * CHUNK)
    idx_max_tf_abs = yf_abs[l_idx:h_idx].argmax() + l_idx
    max_vol_freq = xf[idx_max_tf_abs]
    line_fft.set_ydata(yf_abs)
    hor_line.set_ydata(relative_power)

    if relative_power > VOLUME_THR:
        sound_command = True
        ver_line.set_xdata(max_vol_freq)
        if max_vol_freq > MIDDLE_FREQ:
            direction = True
            ax.set_title('move up')
        else:
            direction = False
            ax.set_title('move down')
    else:
        sound_command = False
        ax.set_title('...')

    # update figure canvas
    try:
        figure.canvas.draw()
        plt.pause(0.05)
        
    except TclError:
        
        print('stream stopped')
        break