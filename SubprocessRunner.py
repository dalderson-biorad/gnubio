#TODO: File headers!

import os
import subprocess
import threading


class SubprocessException(Exception):
    """A simple purpose-branded exception"""
    pass


class SubprocessRunner(object):
    """A class for running one subprocess at a time."""

    def __init__(self):
        """Initializer."""
        self._subproc_lock = threading.Lock()


    def _run_subprocess(self, call):
        """
        Runs subprocesses and throws exceptions on failure.
        Each subprocess call is locked by the same lock so am object can't
        run multiple calls across multiple threads.
        @param call - call to run as a subprocess
        @raise SubprocessException - if subprocess run fails
        """
        with self._subproc_lock: # will unlock even if exception is raised in with block
            try:
                with open(os.devnull, 'w') as FNULL:
                    subprocess.check_call(call, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                raise SubprocessException(e)