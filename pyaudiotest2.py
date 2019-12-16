"""PyAudio Example: Play a WAVE file."""
import time
import pyaudio
import wave
import sys

import numpy as np

CHUNK = 1024
sample_rate = 44100*2


f = 440
t = np.linspace(0, 1, CHUNK)
sin_block = np.sin(np.pi*2*t*f)
stereo_sin_block = np.tile(sin_block, 2).reshape((CHUNK, 2))



def cb(in_data, frame_count, time_info, status_flags):
	print(in_data, frame_count, time_info, status_flags)
	l = frame_count*2*2
	block = bytes(stereo_sin_block)
	return (block ,pyaudio.paContinue)

p = pyaudio.PyAudio()

stream = p.open(format=2,
                channels=2,
                rate=sample_rate,
                output=True,
                stream_callback=cb)


time.sleep(10)
stream.stop_stream()
stream.close()

p.terminate()