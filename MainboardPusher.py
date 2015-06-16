import sys # for exit
from FirmwarePusher import FirmwarePusher
from FirmwarePusher import FirmwarePusherException

# Default serial port for mainboard
PORT_DEFAULT = "/dev/ttyS0"

#Colors for error printing
RED       = '\033[91m'
GREEN     = '\033[92m'
END_COLOR = '\033[0m'


class MainboardPusher(FirmwarePusher):
    """Class for pushing firmware onto the instrument mainboard."""

    def __init__(self, port=PORT_DEFAULT):
        """
        Initializer.
        @param port - serial port connected to arduino master
        """
        super(MainboardPusher, self).__init__(port)


    def _push_master_runtime(self):
         """
        Pushes runtime image to mainboard master
        @raise FirmwarePusherException - if setting master fails
        """
        self._push_master_image("./images/InoArduinoMaster.hex") # can raise


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


def print_ok(msg):
    """Print a happy green status message"""
    print GREEN + msg + END_COLOR


def print_failure(msg):
    """Print an angry red status message"""
    print RED + msg + END_COLOR


if __name__ == "__main__":
    # Parse a provided port
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Serial port for comms with master", default=PORT_DEFAULT)
    args = parser.parse_args()
    port = args.port

    mb_pusher = MainboardPusher(port)
    errors = []

    # If master cant get the pusher, just quit
    try:
        print "Loading pusher on mainboard master..."
        mb_pusher.set_master_as_pusher()
    except FirmwarePusherException as e:
        msg = "Could load pusher on mainboard master: %s" % str(e)
        print_failure(msg)
        print_failure("Terminating early")

    
    push_slaves = { 1 : mb_pusher.push_mainboard_slave_1,
                    2 : mb_pusher.push_mainboard_slave_2,
                    3 : mb_pusher.push_mainboard_slave_3,
                  }

    for number, function in push_slaves:
        try:
            print "Pushing firmware to slave %d..." % number
            function()
        except FirmwarePusherException as e:
            print e
            msg = "Push failed on slave %d: %s" % (d, str(e))
            errors.append(msg)
        
    try:
        print "Loading runtime firmware onto mainboard master..."
        mb_pusher.set_master_as_runtime()

    print ""