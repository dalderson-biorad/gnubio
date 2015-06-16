# TODO: File headers!

import abc # For abstract classes



#python2 gbihexup/src/gbihexup.py --v --port=/dev/ttyS0 --baud=115200 --target=4 --file=images/slave3.hex
#avrdude -C avrdude.conf -v -v -v -p $ATMEL_PART -c wiring -P $COMM_PORT -b $COMM_RATE -D -U flash:w:$HOST_RUNTIME_NAME:i
./firmware/load_host_firmware.sh
./firmware/load_host_runtime.sh


MASTER_LOADER_SCRIPT  = "./firmware/load_master.sh"
AVRDUDE = "avrdude -p atmega2560 -c wiring -b 115200"
AVRDUDE_PORT  = "-P %s"
AVRDUDE_IMAGE = "-D -U flash:w:%s:i"
SLAVE_PUSHER = "python2 gbihexup/src/gbihexup.py --baud=115200" 


class FirmwarePusherException(Exception):
    """A simple purpose-branded exception"""
    pass


class FirmwarePusher(object):
    """An abstract class for pushing firmware over I2C through a master"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, port="/dev/ttys0"):
        """
        Initializer.
        @param port - serial port connected to arduino master
        """
        self._port = port
        self._master_can_push = False


    @staticmethod
    def _run_subprocess(call):
        """
        Runs subprocesses for FirmwarePusher class and throws exceptions on failure.
        @param call - call to run as a subprocess
        @raise FirmwarePusherException - if subprocess fails
        """
        try:
            with open(os.devnull, 'w') as FNULL:
                subprocess.check_call(call, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise FirmwarePusherException(e)


    def _push_master_image(self, image_name):
        """
        Push an image to the master over RS-232.
        @param image_name - filename of the image to push
        @raise FirmwarePusherException - if master push fails
        """
        image_arg = AVRDUDE_IMAGE % image_name
        port_arg  = AVRDUDE_PORT % self._port
        args = " %s %s" % (image_arg, port_arg)
        call = AVRDUDE + args
        FirmwarePusher._run_subprocess(call) # can raise


    def _push_slave_image(self, image_name, i2c_addr):
        """
        Push an image to a slave through the firmware pusher on the master.
        @param image_name - filename of the image to push
        @param i2c_addr - address of the slave on the i2c bus
        @raise FirmwarePusherException - if slave push fails
        """
        if not self._master_can_push:
            msg = "Master has not been set to push firmware"
            raise FirmwarePusherException(msg)
        image_arg = "--file=%s" % image_name
        i2c_arg = "--target=%d" % i2c_addr
        port_arg = "--port=%s" % self._port
        args = " %s %s %s " % (port_arg, i2c_arg, image_arg)
        call = SLAVE_PUSHER + args
        FirmwarePusher._run_subprocess(call) # can raise


    def set_master_as_pusher(self):
        """
        Sets master to be able to push firmware to slaves over I2C.
        @raise FirmwarePusherException - if setting master fails
        """
        self._push_master_image("./images/FirmwarePusher.hex") # can raise
        self._master_can_push = True


    @abc.abstractmethod
    def _push_master_runtime(self):
        """
        Runtime image depends on board type so this must be implemented in children
        @raise NotImplementedError - needs to implemented by children
        """
        raise NotImplementedError


    def set_master_as_runtime(self):
        """
        Sets master to use its runtime image.
        @raise FirmwarePusherException - if setting master fails
        """
        self._push_master_runtime() # can raise
        self._master_can_push = False





class PressurePusher(FirmwarePusher):
    """Class for pushing firmware onto the pressure board."""
    # TODO: work this out after August 2015 deadline
    
    def __init__(self):
        """Initializer for an INCOMPLETE CLASS"""
        # TODO: This isn't done yet!
        raise NotImplementedError