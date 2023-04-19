#!/usr/bin/python

import os
import importlib
from time import time, sleep
import math

import pigpio
import lights
module = lights

config = {

}

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

def start():
	print('start')
	global pi
	pi = pigpio.pi()
	set_freq()
def update():
	print('update')
	set_lights(0, pins['green'])
	set_lights(0, pins['yellow'])
	set_lights(0, pins['orange'])
	set_lights(0, pins['red'])
	set_lights(0, pins['brown'])
	return False
def stop():
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
			status = module.update()
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
			importlib.reload(module)
			module.start()
			finished = False

