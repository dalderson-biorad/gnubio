python2 gbihexup/src/gbihexup.py --v --port=/dev/ttyS0 --baud=115200 --target=4 --file=images/slave3.hex
./firmware/load_host_firmware.sh
./firmware/load_host_runtime.sh


FIRMWARE = "./firmware"
MASTER_PUSHER  = FIRMWARE + "load_master.sh"
SLAVE_PUSHER = "python2 gbihexup/src/gbihexup.py --baud=115200" 



master_images = { "mainboard" : "InoArduinoMaster.hex",
                  "pusher"    : "FirmwarePusher.hex",
                # TODO: PressureMaster can go in here eventually
                }



class FirmwarePusherException(Exception):
    """A simple purpose-branded exception"""
    pass


class FirmwarePusher(object):
    """A class for pushing firmware over I2C through a master"""

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
        image_arg = "-i %s" % image_name
        port_arg  = "-p %s" % self._port
        args = " %s %s" % (image_arg, port_arg)
        call = MASTER_PUSHER + args
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



class MainboardPusher(FirmwarePusher):
    """Class for pusing firmware on the instrument mainboard."""

    def __init__(self, port):
        """
        Initializer.
        @param port - serial port connected to arduino master
        """
        super(MainboardPusher, self).__init__(port)


    # TODO: Can this be pushed a class below?
    def set_master_as_pusher(self):
        """
        Sets master to be able to push firmware to slaves over I2C.
        @raise FirmwarePusherException - if setting master fails
        """
        self._push_master("./images/FirmwarePusher.hex") # can raise
        self._master_can_push = True


    # TODO: Make this an abstract class in the class below
    def set_master_as_runtime(self):
        """
        Sets master to use its runtime image.
        @raise FirmwarePusherException - if setting master fails
        """
        self._push_master("./images/InoArduinoMaster.hex") # can raise
        self._master_can_push = False


    def push_mainboard_slave_1(self):
        """
        Sets master to use its runtime image.
        @raise FirmwarePusherException - if slave firmware can not be pushed
        """
        self._push_slave_image("./images/InoArduinSlave1", 2) # can raise


    def push_mainboard_slave_2(self):
        """
        Sets master to use its runtime image.
        @raise FirmwarePusherException - if slave firmware can not be pushed
        """
        self._push_slave_image("./images/InoArduinSlave2", 3) # can raise


    def push_mainboard_slave_3(self):
        """
        Sets master to use its runtime image.
        @raise FirmwarePusherException - if slave firmware can not be pushed
        """
        self._push_slave_image("./images/InoArduinSlave3", 4) # can raise


