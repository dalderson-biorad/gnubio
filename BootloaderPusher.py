# TODO: File headers!

from enum import Enum
import os
import sys
import subprocess
import threading

#sudo avrdude -p m328p -c avrispmkII -P usb -U bootloaders/atmega328_twi/obj/twi_atmega328p_S4.hex 
#sudo avrdude -p m2560 -c avrispmkII -P usb -U atmega2560_twi/obj/twi_atmega2560_S3.hex
#sudo avrdude -p m2560 -c avrispmkII -P usb -U atmega2560_twi/obj/twi_atmega2560_S2.hex

# avrdude cmd line call and arguments
AVRDUDE = "avrdude -c avrispmkII -P usb"
AVRDUDE_ICE = "/usr/local/bin/avrdude -c atmelice_isp -P usb"
FUSE_SET_2560 = "-e -Ulock:w:0x3F:m -Uefuse:w:0xFD:m -Uhfuse:w:0xD8:m -Ulfuse:w:0xFF:m"
FUSE_SET_328  = "-e -Ulock:w:0x3F:m -Uefuse:w:0x05:m -Uhfuse:w:0xd6:m -Ulfuse:w:0xff:m"
ATMEL_PART = "-p %s"
SLAVE_IMAGE_ARG = "-U %s"
MASTER_IMAGE_ARG = "-Uflash:w:%s:"

# Bootloader hex image location /names
IMAGES_DIR = "./images"
MASTER_BOOTLOADER = IMAGES_DIR + "master_bootloader.hex"
SLAVE1_BOOTLOADER = IMAGES_DIR + "slave1_bootloader.hex"
SLAVE2_BOOTLOADER = IMAGES_DIR + "slave2_bootloader.hex"
SLAVE3_BOOTLOADER = IMAGES_DIR + "slave3_bootloader.hex"

#Colors for error printing
RED       = '\033[91m'
GREEN     = '\033[92m'
END_COLOR = '\033[0m'

# Chip names
ATMEGA_2560 = "m2560"
ATMEGA_328P = "m328p"


class ChipName(Enum):
    """Quick way to differentiate bootload targets"""
    MCB_MASTER = 1
    MCB_SLAVE1 = 2
    MCB_SLAVE2 = 3
    MCB_SLAVE3 = 4


chips = { ChipName.MCB_MASTER : { "part" : ATMEGA_2560, "image" : MASTER_BOOTLOADER, "is_master" : True},
          ChipName.MCB_SLAVE1 : { "part" : ATMEGA_2560, "image" : SLAVE1_BOOTLOADER, "is_master" : False},
          ChipName.MCB_SLAVE2 : { "part" : ATMEGA_2560, "image" : SLAVE2_BOOTLOADER, "is_master" : False},
          ChipName.MCB_SLAVE3 : { "part" : ATMEGA_328P, "image" : SLAVE3_BOOTLOADER, "is_master" : False},
        }


class BootloaderPusherException(Exception):
    """A simple purpose-branded exception"""
    pass


class BootloaderPusher(object):
    """A class for applying bootloaders to on-board arduinos"""


    def __init__(self):
        """TODO"""
        self._subproc_lock = threading.Lock()


    def _run_subprocess(call):
    """
    Runs subprocesses for BootloaderPusher class and throws exceptions on failure.
    Each subprocess call is locked by the same lock so a Bootloader object can't
    run multiple calls across multiple threads.
    @param call - call to run as a subprocess
    @raise FirmwarePusherException - if subprocess fails
    """
    with self._subproc_lock: # will unlock even if exception is raised in with block
        try:
            with open(os.devnull, 'w') as FNULL:
                subprocess.check_call(call, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise BootloaderPusherException(e)


    def _write_fuses(self, part):
        """
        Writes fuses to connected chip
        @param part - type of chip
        @raise BootloaderPusherException - if fuse write fails
        """
        fuses = FUSE_SET_2560 if part = ATMEGA_2560 else FUSE_SET_328
        call = "%s %s" % (AVRDUDE, fuses)
        self._run_subprocess(call) # can raise


    def _write_bootloader(self, part, image, is_master):
        """
        Writes bootloader to connected chip
        @param type - type of chip
        @param image - whether or not target is the master
        @raise BootloaderPusherException - if bootloader write fails
        """
        part_arg = ATMEL_PART % part
        image_arg_base = MASTER_IMAGE_ARG if is_master else SLAVE_IMAGE_ARG
        image_arg = image_arg_base % image
        args = " %s %s " % (part_arg, image_arg)
        call = AVRDUDE + args
        self._run_subprocess(call) #can raise


    def _prepare_processor(self, chip):
        """
        Write fuses and bootloader to selected processor
        @param which_processor - which on-board chip to write
        @raise BootloaderPusherException - If unsupported chip or if preparation fails
        """
        if chip not in chips:
            msg = "%s is not a valid processor" % which_processor
            raise BootloaderPusherException(msg)
        chip_info = chips[chip]
        part      = chip_info['part']
        image     = chip_info['image']
        is_master = chip_info['is_master']
        write_fuses(part) # can raise
        write_bootloader(part, image, is_master) # can raise


    def bootload_master(self):
        self._prepare_processor(ChipName.MCB_MASTER)
            

    def bootload_slave1(self):
        self._prepare_processor(ChipName.MCB_SLAVE1)


    def bootload_slave2(self):
        self._prepare_processor(ChipName.MCB_SLAVE2)


    def bootload_slave3(self):
        self._prepare_processor(ChipName.MCB_SLAVE3)



def print_ok(msg):
    """Print a happy green status message"""
    print GREEN + msg + END_COLOR


def print_failure(msg):
    """Print an angry red status message"""
    print RED + msg + END_COLOR


if __name__ == "__main__":
    # Check for super user priveledges
    if os.getuid() != 0:
        import __main__
        print_failure("Needs to run with super user priveledges!")
        print "Please re-run as: sudo %s" % __main__.__file__
        sys.exit(1)


