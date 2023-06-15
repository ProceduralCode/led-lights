#!/usr/bin/python

import os
import importlib
from time import time, sleep
import math
from datetime import datetime as dt

import pigpio
import lights
module = lights

schedule = {
	0:     (0, 0, 0),
	7:     (0, 0, 0),
	8:     (1, 0, 0),
	9:     (1, 1, 0),
	1 +12: (1, 1, 1),
	6 +12: (1, 1, 0),
	7 +12: (1, 0, 0),
	8 +12: (1/25, 0, 0),
}
update_inter = 1/60

info = False
simulated_time = None
cycling_test = None
test_color = None
# test_color = (0.1, 0.1, 0.1)
# test_color = (1, 1, 1)

pins = {
	'black':  2,
	'white':  3,
	'grey':   4,
	'purple': 14,
	'blue':   15,
	'green':  18,
	'yellow': 17,
	'orange': 27,
	'red':    22,
	'brown':  23,
}

# Info
	# Install
		# sudo apt-get install build-essential unzip wget
		# wget https://github.com/joan2937/pigpio/archive/master.zip
		# unzip master.zip
		# cd pigpio-master
		# make
		# sudo make install
	# Cmds
		# sudo pigpiod -s 1    # start daemon with 1us sampling rate
		# sudo killall pigpiod # (to stop daemon)
	# Docs
		# pins:    https://pinout.xyz
		# pigpiod: https://abyz.me.uk/rpi/pigpio/pigpiod.html
		# pigs:    https://abyz.me.uk/rpi/pigpio/pigs.html
		# pigpio:  https://abyz.me.uk/rpi/pigpio/python.html

def lerp(a, b, t):
	if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
		return tuple(lerp(a[i], b[i], t) for i in range(len(a)))
	return a + (b-a)*t

def start():
	if info:
		print('start')
	if not os.popen('ps -Af').read().count('pigpiod'):
		raise Exception('pigpiod not running')
	global pi
	pi = pigpio.pi()
	set_freq()
def update():
	global simulated_time
	if info:
		print('update')
	# wnc = (0.1, 0.1, 0.1)
	# wnc = (1, 1, 0.7)
	# wnc = (0.5, 0.1, 0)
	if cycling_test:
		simulated_time = time() % 24

	# hour of the day (with decimal)
	now = simulated_time
	if simulated_time is None:
		now = dt.now().hour + dt.now().minute/60 + dt.now().second/3600

	# interpolate between two closest times in schedule
	times = list(schedule.keys())
	times.sort()
	idx2 = 0
	while idx2 < len(times) and times[idx2] <= now:
		idx2 += 1
	if idx2 == len(times):
		idx2 = 0
	if idx2 == 0:
		idx1 = -1
	else:
		idx1 = idx2-1
	t1 = times[idx1]
	t2 = times[idx2]
	a = schedule[t1]
	b = schedule[t2]
	if t1 > t2:
		t2 += 24
	t = (now - t1) / (t2 - t1)
	wnc = lerp(a, b, t)
	if test_color:
		wnc = test_color

	# set_lights(0, pins['black'])
	# set_lights(0, pins['white'])
	set_lights(wnc[2], pins['grey'])
	set_lights(wnc[1], pins['purple'])
	set_lights(wnc[0], pins['blue'])
	# set_lights(0, pins['green'])
	set_lights(0, pins['yellow'])
	set_lights(wnc[0], pins['orange'])
	set_lights(wnc[1], pins['red'])
	set_lights(wnc[2], pins['brown'])

	set_lights(wnc[0], pins['white'])
	set_lights(wnc[1], pins['black'])
	set_lights(wnc[2], pins['green'])

	sleep(update_inter)
	# return True # stop
def stop():
	if info:
		print('stop')
	pi.stop()

def set_freq(hz=2500, pin=None):
	# Available options: 40000 20000 10000 8000 5000 4000 2500 2000 1600 1250 1000 800 500 400 250 200 100 50
	# Note: higher frequencies have lower resolution of brightness levels (try setting to 1/255)
	# https://abyz.me.uk/rpi/pigpio/python.html#set_PWM_frequency
	for pin in ([pin] if pin else pins.values()):
		pi.set_PWM_frequency(pin, int(hz))
def set_lights(amt, pin=None):
	pins = [pin] if pin else pins.values()
	for pin in pins:
		amt = min(1, max(0, amt)) # clip to 0-1
		pi.set_PWM_dutycycle(pin, int(amt*255))
def wave_test():
	t = time()
	end = t + 10
	while t < end:
		top = 0.3
		set_lights((math.sin(t) + 1)/2 * top, pins['green'])
		sleep(1/240)
		t = time()

if __name__ == '__main__':
	last_mod = os.path.getmtime(__file__)
	last_check = 0
	module.start()
	finished = False
	while True:
		if finished:
			sleep(0.1)
		else:
			status = module.update() # return None if not finished
			finished = False if status is None else True
			if finished:
				module.stop()
			if time() - last_check < 0.1:
				continue
		mod = os.path.getmtime(__file__)
		if mod - last_mod > 0.1:
			last_mod = mod
			if not finished:
				module.stop()
			sleep(1)
			importlib.reload(module)
			module.start()
			finished = False

