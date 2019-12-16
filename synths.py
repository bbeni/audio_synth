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
        self.base_freq = 440*4
        self.sample_rate = sample_rate
        self.chunk = chunk_size

        self.notes_on = {}

        self._gen_wavetable()
        self.max_amp = max([np.max(w) for w in self.wavetable.values()])
        print("max amp is:", self.max_amp)


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

            #overtones
            for d in range(2,16):
                wave += np.sin(freq/d*t)*1/d

            print(T, n_samples, len(wave))


    def play_note(self, nr):
        self.notes_on[nr] = 0

    def end_note(self, nr):
        del self.notes_on[nr]

    def update(self, frame_count, time_info):
        audio_chunk = np.zeros((self.chunk))
        for note, offset in self.notes_on.items():
            wave = self.wavetable[note]
            l = len(wave)
            audio_chunk += np.tile(wave, 2)[offset:self.chunk+offset]
            offset = (offset+self.chunk)%l
            self.notes_on[note] = offset

        #stereo
        audio_chunk = np.repeat(audio_chunk, 2)

        n_notes_on = len(self.notes_on)
        if n_notes_on > 0:
            audio_chunk *= np.iinfo(np.int32).max*0.7 / n_notes_on / self.max_amp

        self.frames = bytes(audio_chunk.astype(np.int32))
