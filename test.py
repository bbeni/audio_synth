import numpy as np
from scipy import signal
import simpleaudio as sa

# calculate note frequencies
A_freq = 440

octave_freq = [A_freq * 2 ** (i/12) for i in range(12)]


# get timesteps for each sample, T is note duration in seconds
sample_rate = 44100
T = 10
t = np.linspace(0, T, T * sample_rate, False)
t = np.tan(t)

# generate sine wave notes
A_note = np.sin(A_freq * t * 2 * np.pi)

sin_notes = [np.sin(f*t*2*np.pi) for f in octave_freq]
saw_notes = [signal.sawtooth(f*t*2*np.pi) for f in octave_freq]
weird_notes = [signal.sawtooth(f*t*2*np.pi)*0.5 - 
        for f in octave_freq]


saw_wave = signal.sawtooth(2 * np.pi * A_freq * t) 
square_wave = signal.square(2 * np.pi * A_freq * t) 
modulation = np.sin(2*np.pi*1.34 * t)


# mix audio together
#audio = np.zeros((int(T*44100), 2))
#n = len(t)
#offset = 0
#audio[0 + offset: n + offset, 0] += square_wave
#audio[0 + offset: n + offset, 0] *= modulation

audio = np.zeros((int(T*44100), 2))
n = len(t)
l = int(n/12)
print(l)

for i in range(12):
    audio[0+i*l: l+i*l, 0] += saw_notes[i][0:l]



# normalize to 16-bit range
audio *= 32767 / np.max(np.abs(audio))
# convert to 16-bit data
audio = audio.astype(np.int16)

# start playback
play_obj = sa.play_buffer(audio, 2, 2, sample_rate)

# wait for playback to finish before exiting
play_obj.wait_done()
