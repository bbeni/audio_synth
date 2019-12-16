"""PyAudio Example: Play a WAVE file."""
import time

import pyaudio
import wave
import sys

import numpy as np
from scipy import signal

import matplotlib.pyplot as plt


class Synth:
    def __init__(self, sample_rate, chunk_size):
        self.wavetable = {}
        self.base_freq = 440
        self.sample_rate = sample_rate
        self.chunk = chunk_size

        self.notes_on = {}

        self._gen_wavetable()

        self.__pyaudio = pyaudio.PyAudio()
        self.stream = self.__pyaudio.open(format=2,
                channels=2,
                rate=sample_rate,
                output=True)

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()

        self.__pyaudio.terminate()

    def _gen_wavetable(self):
        for i, note in enumerate(range(36,84+1)):
            freq = self.base_freq * 2 ** (i/12)

            T = 2*np.pi/freq
            n_samples = T*self.sample_rate
            while n_samples < self.chunk:
                T *= 2
                n_samples = T*self.sample_rate
 
            t = np.linspace(0, T, n_samples)
            wave = np.sin(freq*t)
            self.wavetable[note] = wave

            #plt.plot(t, wave)
            #plt.show()

            print(T, n_samples, len(wave))


    def play_note(self, nr):
        self.notes_on[nr] = 0

    def end_note(self, nr):
        del self.notes_on[nr]

    def update(self):
        audio_chunk = np.zeros((self.chunk, 2))
        for note, offset in self.notes_on.items():
            wave = self.wavetable[note]
            l = len(wave)
            audio_chunk[:,0] += np.tile(wave, 2)[offset:self.chunk+offset]
            offset = (offset+self.chunk-1)%l
            self.notes_on[note] = offset

        #stereo
        audio_chunk[:,1] = audio_chunk[:,0]
        
        audio_chunk *= 32766 / np.max(np.abs(audio_chunk))
        data = audio_chunk.astype(np.int16)

        self.stream.write(bytes(data))



synth = Synth(44100, 1024)
synth.play_note(60)
for i in range(100):
    synth.update()
time.sleep(1)
synth.end_note(60)
del synth