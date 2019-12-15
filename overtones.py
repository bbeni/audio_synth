import numpy as np
from scipy import signal
import pygame, pygame.sndarray

import matplotlib.pyplot as plt

def play_for(sample_wave, ms):
    """Play the given NumPy array, as a sound, for ms milliseconds."""
    sound = pygame.sndarray.make_sound(sample_wave)
    sound.play(-1)
    pygame.time.delay(ms)
    sound.stop()

# calculate note frequencies
A_freq = 440

octave_freq = [A_freq * 2 ** (i/12) for i in range(12)]
overtone_freq = [A_freq * i for i in range(1,16)]


# get timesteps for each sample, T is note duration in seconds
sample_rate = 44100
T = 10
t = np.linspace(0, T, T * sample_rate, False)

# generate sine wave notes
A_note = np.sin(A_freq * t * 2 * np.pi)

sin_notes = [np.sin(f*t*2*np.pi) for f in overtone_freq]
saw_notes = [signal.sawtooth(f*t*2*np.pi) for f in octave_freq]
weird_notes = [signal.sawtooth(f*t*2*np.pi)*0.5 for f in octave_freq]


saw_wave = signal.sawtooth(2 * np.pi * A_freq * t) 
square_wave = signal.square(2 * np.pi * A_freq * t) 


# mix audio together
#audio = np.zeros((int(T*44100), 2))
#n = len(t)
#offset = 0
#audio[0 + offset: n + offset, 0] += square_wave
#audio[0 + offset: n + offset, 0] *= modulation



audio = np.zeros((int(T*44100), 2))
n = len(t)
l = int(n/12)

# envelope
attack = int(l/2)
env = [x/attack for x in range(attack)] + [1 for _ in range(l-attack)]

for i in range(12):
    audio[0+i*l: l+i*l, 0] += sin_notes[i][0:l]*env

#stereo
audio[:,1] = audio[:,0]

#lfo
modulation = np.sin(2*np.pi*0.6 * t)
audio[:,0] *= modulation
modulation = np.cos(2*np.pi*0.6 * t)
audio[:,1] *= modulation


# normalize to 16-bit range
audio *= 32767 / np.max(np.abs(audio))
# convert to 16-bit data
audio = audio.astype(np.int16)
audio = audio.copy(order="C")


pygame.mixer.init()
play_for(audio, 8000)


