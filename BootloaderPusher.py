#! /usr/bin/python
# TODO: File headers!


import argparse
from enum import Enum
import os
import sys
from SubprocessRunner import SubprocessRunner, SubprocessException

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
MASTER_IMAGE_ARG = "-Uflash:w:%s:i -Ulock:w:0x0F:m"

# Bootloader hex image location /names
IMAGES_DIR = "images/"
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


class BootloaderPusher(SubprocessRunner):
    """A class for applying bootloaders to on-board arduinos"""

    def __init__(self, use_ice=False):
        """
        Initializer.
        @param use_ice - use Atmel ice (white rectangle) AVR programmer.
        """
        #TODO - make sudo checking done in init
        super(BootloaderPusher, self).__init__()
        self._avrdude_cmd = AVRDUDE_ICE if use_ice else AVRDUDE


    def _write_fuses(self, part):
        """
        Writes fuses to connected chip
        @param part - type of chip
        @raise BootloaderPusherExcepdtion - if fuse write fails
        """
        part_arg = ATMEL_PART % part
        fuses = FUSE_SET_2560 if part == ATMEGA_2560 else FUSE_SET_328
        args = " %s %s " % (part_arg, fuses)
        call = self._avrdude_cmd + args
        try:
            self._run_subprocess(call)
        except SubprocessException as e:
            raise BootloaderPusherException(e)


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
        call = self._avrdude_cmd + args
        try:
            self._run_subprocess(call)
        except SubprocessException as e:
            raise BootloaderPusherException(e)


    def _prepare_processor(self, chip):
        """
        Write fuses and bootloader to selected processor
        @param which_processor - which on-board chip to write
        @raise BootloaderPusherException - If unsupported chip or if preparation fails
        """
        if chip not in chips:
            msg = "%s is not a valid processor" % chip
            raise BootloaderPusherException(msg)
        chip_info = chips[chip]
        part      = chip_info['part']
        image     = chip_info['image']
        is_master = chip_info['is_master']
        self._write_fuses(part) # can raise
        self._write_bootloader(part, image, is_master) # can raise


    def bootload_master(self):
        """
        Write fuses and bootloader to mainboard master.
        @raise BootloaderPusherException - if fuse / bootload prep fails
        """
        self._prepare_processor(ChipName.MCB_MASTER)


    def bootload_slave1(self):
        """
        Write fuses and bootloader to mainboard master.
        @raise BootloaderPusherException - if fuse / bootload prep fails
        """
        self._prepare_processor(ChipName.MCB_SLAVE1)


    def bootload_slave2(self):
        """
        Write fuses and bootloader to mainboard master.
        @raise BootloaderPusherException - if fuse / bootload prep fails
        """
        self._prepare_processor(ChipName.MCB_SLAVE2)


    def bootload_slave3(self):
        """
        Write fuses and bootloader to mainboard master.
        @raise BootloaderPusherException - if fuse / bootload prep fails
        """
        self._prepare_processor(ChipName.MCB_SLAVE3)


def print_ok(msg):
    """Print a happy green status message"""
    print GREEN + msg + END_COLOR


def print_failure(msg):
    """Print an angry red status message"""
    print RED + msg + END_COLOR


def one_bootload(name, function):
    """
    Helper function to the console based bootloader pusher utility.
    @param name - name of device to target
    @param function - function to write fuses and bootloader to device
    """
    quit_str = 'quit'
    request = "Type '%s' when ready to proceed (or quit to %s up): " % (name, quit_str)

    while(1):
        print "Please attach programmer tool to %s" % name
        response = raw_input(request)

        if response == quit_str:
            return False
        elif response != name:
            print "%s is not a valid option" % response
            continue

        try:
            print "Setting fuses and applying bootloader to %s..." % name
            function()
        except BootloaderPusherException as e:
            print "Could not bootload %s: %s" % (name, str(e))
            continue
        break
    return True


if __name__ == "__main__":
    # Check for super user priveledges
    if os.getuid() != 0:
        import __main__
        print_failure("Needs to run with super user priveledges!")
        print "Please re-run as: sudo python %s" % __main__.__file__
        sys.exit(1)

    # Parse a provided port
    device_help = "Device to bootload"
    ice_help = "Use atmel ice programmer (not fully supported yet...)"
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", help=device_help, default=None)
    parser.add_argument("-i", "--use_ice", action='store_true', help=ice_help, default=False)
    args = parser.parse_args()
    device = args.device
    use_ice = args.use_ice

    b_push = BootloaderPusher(use_ice)
    loads = { "master" : b_push.bootload_master,
              "slave1" : b_push.bootload_slave1,
              "slave2" : b_push.bootload_slave2,
              "slave3" : b_push.bootload_slave3,
            }

    if device != None:
        if device not in loads:
            print "%s is not a valid target for bootloading!" % device
            print "Please use one of these:"
            print loads.keys()
            sys.exit(1)
        result = one_bootload(device, loads[device])
        if not result:
            print "Could not complete %s" % device
            sys.exit(1)
        print_ok("Bootloaded %s successfully" % device)
        sys.exit(0)

    for name, function in sorted(loads.items()):
        result = one_bootload(name, function)
        if not result:
            print "Could not complete %s" % name
            sys.exit(1)
    print_ok("Bootloaded all successfully")
    sys.exit(0)
