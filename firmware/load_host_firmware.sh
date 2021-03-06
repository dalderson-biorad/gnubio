#!/bin/sh
#
# Simple script, loads the GNUBio Host Loader into the Host controller
# on the GNUBio PCB Assembly.
#
# Prerequisits:
#	1. Host conntroller is pre-programmed with the Arduino Bootloader.
#


ATMEL_PART=atmega2560
COMM_PORT=/dev/ttyS0
COMM_RATE=115200


HOST_LOADER_PATH=~/dalderson/pusher/firmware/mega2560/gnubio_host_loader/obj
HOST_LOADER_NAME=$HOST_LOADER_PATH/gnubio_host_loader.cpp.hex

ARDUINO_HOME=~/bin/arduino-1.0.6
ARDUINO_TOOLS=$ARDUINO_HOME/hardware/tools


#$ARDUINO_TOOLS/avrdude -C $ARDUINO_TOOLS/avrdude.conf -v -v -v -p $ATMEL_PART -c wiring -P $COMM_PORT -b $COMM_RATE -D -U flash:w:$HOST_LOADER_NAME:i
avrdude -C avrdude.conf -v -v -v -p $ATMEL_PART -c wiring -P $COMM_PORT -b $COMM_RATE -D -U flash:w:$HOST_LOADER_NAME:i


