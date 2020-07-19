#!/bin/bash

export LD_LIBRARY_PATH=/usr/local/lib
export PYTHONPATH="/home/pi/.local/lib/python2.7/site-packages"
ldconfig

usbmuxd

gpio mode 21 in
gpio mode 21 down

gpio mode 22 in
gpio mode 22 down

gpio mode 24 in
gpio mode 24 down

gpio mode 25 in
gpio mode 25 down

gpio mode 27 in
gpio mode 27 down

gpio mode 28 in
gpio mode 28 down

gpio mode 29 in
gpio mode 29 down

python main.py
