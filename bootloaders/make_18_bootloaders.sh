#! /usr/bin/env bash

BUILDNAME="twi_atmega328p_SX.hex"
OUTPUT_NAME="new_slaveX.hex"
OUTPUT_DIR="NewBootloaders"
USR_TOOLPATH="/usr/bin"
USR_ISPPATH-"/usr/bin"

pushd atmega328_twi

# Create dir if it doesn't exit, empty it if it does
if [ ! -d "../$OUTPUT_DIR" ]
then
    mkdir ../$OUTPUT_DIR
else
    rm -rf ../$OUTPUT_DIR/*.hex
fi

# Loop over bootloaders by i2c addr
for slave in `seq 0 17`
do
    ic2_addr=$(($slave+1)) # i2c_addr is always 1 higher than slave number
    make clean
    make SLAVE_ID=$ic2_addr # TOOLPATH=$USR_TOOLPATH ISPPATH=$USR_ISPPATH
    mv obj/${BUILDNAME/X/$ic2_addr} ../$OUTPUT_DIR/${OUTPUT_NAME/X/$slave}
done

popd