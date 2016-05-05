#! /usr/bin/env bash

BUILDNAME="twi_atmega328p_SX.hex"
PRESSNAME="pressure_slaveX.hex"
PRESSDIR="PressureBootloaders"
USR_TOOLPATH="/usr/bin"
USR_ISPPATH-"/usr/bin"

pushd atmega328_twi

# Create dir if it doesn't exit, empty it if it does
if [ ! -d "../$PRESSDIR" ]
then
    mkdir ../$PRESSDIR
else
    rm -rf ../$PRESSDIR/*.hex
fi


rm -rf ../$PRESSDIR/*

for slave in `seq 0 17`
do
    ic2_addr=$(($slave+1)) # i2c_addr is always 1 higher than slave number
    make clean
    make SLAVE_ID=$ic2_addr TOOLPATH=$USR_TOOLPATH ISPPATH=$USR_ISPPATH OPTIMIZE=1
    mv obj/${BUILDNAME/X/$ic2_addr} ../$PRESSDIR/${PRESSNAME/X/$slave}
done

popd