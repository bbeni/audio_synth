"""PyAudio Example: Play a WAVE file."""

import pyaudio
import wave
import sys

import numpy as np

CHUNK = 1024
sample_rate = 44100*2

p = pyaudio.PyAudio()

stream = p.open(format=2,
                channels=2,
                rate=sample_rate,
                output=True)


T = 20
t = np.linspace(0, T, T * sample_rate, False)
n = len(t)
print(n)

basef = 55
octave_freq = [basef * 2 ** (i/12) for i in range(13)]



for i in range(1,13):
    overtone_freq = [octave_freq[i-1] * j for j in range(1,25)]
    sin_notes = [np.sin(f*t*2*np.pi) for f in overtone_freq]


    audio = np.zeros((int(T*sample_rate), 2))

    l = int(n/25)

    for j in range(24):
        print(j)
        audio[0+j*l:, 0] += 1/(j**1.4+2)*sin_notes[j][j*l:]


    lfo = np.sin(np.sin(np.log(i)/2*t**(i/2+1/2)*2*np.pi))

    audio[:,0] += 0.6*audio[:,0]*lfo
    #audio[:,0] -= 0.12*audio[::-1,0]

    ## reverb
    audio[8820:,0] += 0.3*audio[:-8820,0]
    audio[5500:,0] += 0.3*audio[:-5500,0]
    #audio[100:,0] += 0.2*audio[:-100,0]
    #audio[150:,0] += 0.15*audio[:-150,0]
    #audio[200:,0] += 0.1*audio[:-200,0]

    #stereo
    audio[:,1] = audio[:,0]
    audio *= 32767 / np.max(np.abs(audio))
    data = audio.astype(np.int16)

    import time
    xd = time.time()
    for i in range(int(len(data)/CHUNK)):
    	#stream.write(data[i*CHUNK:(i+1)*CHUNK])
    	l = data[i*CHUNK:(i+1)*CHUNK]
    	stream.write(bytes(l))
    print(time.time() - xd)



stream.stop_stream()
stream.close()

p.terminate()