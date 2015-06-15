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
HEX_IMAGE_LOC=./images
HEX_IMAGE=UNDEFINED


#ARDUINO_HOME=~/bin/arduino-1.0.6
#ARDUINO_TOOLS=$ARDUINO_HOME/hardware/tools


usage() {
    echo "Push an image to the I2C master over RS-232"
    echo
    echo "ARGUMENTS:"
    echo "  -h This screen."
    echo "  -p Comm port (default /dev/ttyS0)"
    echo "  -i hex image file to push to the master"
    echo
}


while getopts ":p:i:h" opt; do
    case $opt in
        p)
            COMM_PORT=$OPTARG 
            ;;
        i)
            HEX_IMAGE=$OPTARG 
            ;;
        h)
            usage
            exit 0
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            exit 1
            ;;
    esac
done

#echo $HEX_IMAGE_LOC/$HEX_IMAGE
#echo $COMM_PORT

#$ARDUINO_TOOLS/avrdude -C $ARDUINO_TOOLS/avrdude.conf -v -v -v -p $ATMEL_PART -c wiring -P $COMM_PORT -b $COMM_RATE -D -U flash:w:$HOST_RUNTIME_NAME:i
#avrdude -C avrdude.conf -v -v -v -p $ATMEL_PART -c wiring -P $COMM_PORT -b $COMM_RATE -D -U flash:w:$HOST_RUNTIME_NAME:i

avrdude -C avrdude.conf -v -v -v -p atmega2560 -c wiring -P /dev/ttyS0 -b 115200 -D -U flash:w:PressureMaster.hex:i

