#!/bin/bash

if [ "$EUID" -ne 0 ]
	then echo "Please run as root"
	exit
fi

# start daemon
pigpiod -s 1

# run without su priv
sudo -u pi nohup ./lights.py >&/dev/null &
