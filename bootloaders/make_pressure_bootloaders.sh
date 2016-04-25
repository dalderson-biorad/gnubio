#! /usr/bin/env bash

BUILDNAME="twi_atmega328p_SX.hex"
PRESSNAME="pressure_slaveX.hex"
PRESSDIR="PressureBootloaders"

pushd atmega328_twi

# TODO: Check if dir already exists
if [ ! -d "../$PRESSDIR" ]
then
    mkdir ../$PRESSDIR
fi

for slave in `seq 0 17`
do
    make SLAVE_ID=$slave
    mv obj/${BUILDNAME/X/$slave} ../$PRESSDIR/${PRESSNAME/X/$slave}
done

popd