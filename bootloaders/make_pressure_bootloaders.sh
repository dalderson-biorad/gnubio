#! /usr/bin/env bash

BUILDNAME="twi_atmega328p_SX.hex"
PRESSNAME="pressure_slaveX.hex"
PRESSDIR="PressureBootloaders"
USR_TOOLPATH="/usr/bin"
USR_ISPPATH-"/usr/bin"

pushd atmega328_twi

# TODO: Check if dir already exists
if [ ! -d "../$PRESSDIR" ]
then
    mkdir ../$PRESSDIR
fi

for slave in `seq 0 17`
do
    ic2_addr=$(($slave+1)) # i2c_addr is always 1 higher than slave number
    make SLAVE_ID=$ic2_addr TOOLPATH=$USR_TOOLPATH ISPPATH=$USR_ISPPATH
    mv obj/${BUILDNAME/X/$slave} ../$PRESSDIR/${PRESSNAME/X/$slave}
done

popd