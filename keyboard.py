import time
import threading
import queue

import numpy as np

import pyaudio
import mido

from synths import Synth


print('output devices:', mido.get_output_names())
print('input devices:', mido.get_input_names())

highes = 84
lowest = 36

midi_queue = queue.Queue()

def midi_handler():
	with mido.open_input('UM-1 0') as keyboard:
		for msg in keyboard:
			midi_queue.put(msg)
			print(msg)

x = threading.Thread(target=midi_handler, args=(), daemon=True)
x.start()


sample_rate = 44100
chunk_size = 1024
TIME_PER_FRAME = 1/(sample_rate/chunk_size)


synth = Synth(sample_rate, chunk_size)
synth.update(None, None)

def audio_callback(in_data, frame_count, time_info, status_flags):
	#print(in_data, frame_count, time_info, status_flags)
	global synth
	synth.update(frame_count, time_info)
	block = synth.frames
	return (block, pyaudio.paContinue)

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt32,
                channels=2,
                rate=sample_rate,
                output=True,
                stream_callback=audio_callback)

while True:
	#print(midi_queue.qsize())
	#consume midi
	while not midi_queue.empty():
		midi_msg = midi_queue.get_nowait()
		print(midi_msg)
		if midi_msg.type == 'note_on':
			if midi_msg.velocity > 0:
				synth.play_note(midi_msg.note)
			else:
				synth.end_note(midi_msg.note)

	time.sleep(0.05)




time.sleep(1)
stream.stop_stream()
stream.close()

p.terminate()
