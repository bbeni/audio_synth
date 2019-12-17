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
        
        # adsr in units if chunk_size/samplerate ~ 1/40 second
        self.attack = 2
        self.decay = 20
        self.sustain = 0.64
        self.release = 2

        self.attack_env = np.linspace(0, 1, chunk_size*self.attack)
        self.decay_env = np.linspace(1, self.sustain, chunk_size*self.decay)
        self.release_env = np.linspace(self.sustain, 0, chunk_size*self.release)
        self.notes_envelope = {}

        self.wavetable = {}
        self.base_freq = 55
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size

        self.notes_on = {}

        self._gen_wavetable()
        self.max_amp = max([np.max(w) for w in self.wavetable.values()])
        print("max amp is:", self.max_amp)

    def _gen_wavetable(self):
        for i, note in enumerate(range(36,84+1)):

            freq = self.base_freq * 2 ** (i/12)
            # quantize the frequency, such that it matches the sample rate
            # 1/f = n*(1/sample rate)
            n = self.sample_rate/freq
            freq = self.sample_rate/int(round(n))

            n_samples = 1/freq * self.sample_rate - 1

            T = 1/freq

            #print(freq)
            #print(n_samples)
            #print(T)

            a = False
            while n_samples < self.chunk_size:
                T *= 2
                n_samples = T*self.sample_rate
                a = True
 
            t = np.linspace(0, T*(1-1/n_samples), n_samples)
            wave = np.sin(freq*t*2*np.pi)
            self.wavetable[note] = wave

            #overtones
            piano = [0.1, 0.33, 0.075, 0.065, 0.06, 0, 0.025, 0, 0, 0, 0, 0.01]
            guitar = [0.7, 1.25, 0.15, 0.15, 0.13, 0, 0.01, 0.2, 0.07, 0.02]
            for d, coeff in zip(range(2,16), piano):
                wave += np.sin(freq*d*t*2*np.pi)*coeff
                #plt.plot(t, np.sin(freq*d*t*2*np.pi))
                #plt.show()

            #print(np.tile(wave, 2).shape)

            if False:
                plt.plot(np.linspace(0,T*2,2*n_samples), np.tile(wave, 2))
                plt.show()

            #print(T, n_samples, len(wave))


    def play_note(self, note):
        self.notes_on[note] = 0
        self.notes_envelope[note] = ('attack', 0)

    def next_env(self, note):
        c_size = self.chunk_size

        # bad...
        if not note in self.notes_envelope:
            return 0

        status, t = self.notes_envelope[note]
        if status == 'attack':
            if t == self.attack-1:
                self.notes_envelope[note] = ('decay', 0)
            else:
                self.notes_envelope[note] = ('attack', t+1)
            return self.attack_env[t*c_size:(t+1)*c_size]
        if status == 'decay':
            if t == self.decay-1:
                self.notes_envelope[note] = ('sustain', 0)
            else:
                self.notes_envelope[note] = ('decay', t+1)
            return self.decay_env[t*c_size:(t+1)*c_size]
        if status == 'sustain':
            return self.sustain
        if status == 'release':
            if t == self.release:
                del self.notes_on[note]
                del self.notes_envelope[note]
                return 0
            else:
                self.notes_envelope[note] = ('release', t+1)
            return self.release_env[t*c_size:(t+1)*c_size]

    def dirty_hack(self):
        # bad fix for a bug
        k1 = list(self.notes_on.keys())
        k2 = list(self.notes_envelope.keys())

        for k in k1:
            if not k in k2: del self.notes_on[k]

        for k in k2:
            if not k in k1: del self.notes_on[k]


    def end_note(self, note):
        self.notes_envelope[note] = ('release', 0)
        
    def update(self, frame_count, time_info):
        audio_chunk = np.zeros((self.chunk_size))
        for note, offset in list(self.notes_on.items()):
            wave = self.wavetable[note]
            l = len(wave)
            #print(note, offset)

            env = self.next_env(note)

            audio_chunk += np.tile(wave, 2)[offset:self.chunk_size+offset]*env
            offset = (offset+self.chunk_size)%l
            self.notes_on[note] = offset

        self.dirty_hack()

        #stereo
        audio_chunk = np.repeat(audio_chunk, 2)
        

        # just for fun xD
        _, _, Zxx = signal.stft(audio_chunk.reshape((int(self.chunk_size/16), 32)))
        _, xrec = signal.istft(Zxx)
        xrec = -0.8*xrec*np.sin(np.linspace(0,10*np.pi,self.chunk_size*2).reshape(xrec.shape))
        xrec = xrec*np.sin(np.linspace(0,2*np.pi,self.chunk_size*2).reshape(xrec.shape))
        audio_chunk = xrec.reshape((self.chunk_size*2))

        ##reverb
        #audio_chunk[5:] += 0.2*audio_chunk[:-5] 
        #audio_chunk[9:] += 0.3*audio_chunk[:-9] 
        #audio_chunk[30:] += 0.4*audio_chunk[:-30]
        #audio_chunk *= 0.5

        ## smoothing
        #box_pts = 40
        #box = np.ones(box_pts)/box_pts
        #audio_chunk = np.convolve(audio_chunk, box, mode='same')

        n_notes_on = len(self.notes_on)
        if n_notes_on > 0:
            audio_chunk *= np.iinfo(np.int32).max*0.7 / n_notes_on / self.max_amp


 

        self.frames = bytes(audio_chunk.astype(np.int32))
