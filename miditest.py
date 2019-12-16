import time
import threading
import queue

import mido


print('output devices:', mido.get_output_names())
print('input devices:', mido.get_input_names())

highes = 84
lowest = 38

midi_queue = queue.Queue()


def midi_handler():
	with mido.open_input('UM-1 0') as keyboard:
		for msg in keyboard:
			midi_queue.put(msg)

x = threading.Thread(target=midi_handler, args=(), daemon=True)
x.start()



sample_rate = 44100
chunk_size = 1024
TIME_PER_FRAME = 0.007

curr_time = time.time()
while True:
	#print(midi_queue.qsize())
	#consume midi
	while not midi_queue.empty():
		a = midi_queue.get_nowait()
		print(a)




	#### does not work how i want it....
	last_time = curr_time
	curr_time = time.time()
	elapsed = curr_time - last_time
	print(elapsed)
	time_to_sleep = TIME_PER_FRAME - elapsed
	if time_to_sleep > 0:
		time.sleep(time_to_sleep)

	else:
		#print("Warning: loop took too long!")
		#print(elapsed)
		pass



