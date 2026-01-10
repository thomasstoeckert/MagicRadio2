"""
    This file contains the thread class for the operation of reading inputs and saving them to the globals object
"""
import MRGlobals
import threading
import random
import logging
import time
import json

"""
    Input Control talks to the arduino, picking up the latest full line and parsing it
"""

# readThread is just there to read the latest line from serial however fast the MRGlobals clock says.
class readThread (threading.Thread):
    def __init__(self, serial):
        threading.Thread.__init__(self)
        self.serial = serial

    def run(self):
        buffer_string = ''
        logging.debug("ReadThread has begun")
        while MRGlobals.running:
            # This whole mess just waits for a full message, gets the most recent one, and formats it
            buffer_string = buffer_string + self.serial.read(self.serial.inWaiting())
            if '\n' in buffer_string:
                lines = buffer_string.split('\n')
                MRGlobals.lastLineReceived = lines[-2]
                buffer_string = lines[-1]
                split_last = MRGlobals.lastLineReceived.split(',')
                try:
                    # split_last is formatted "tuningInt,volumeInt,volumeOn" with tuningInt and volumeInt ranging from 0 - 1023, 
                    #  and volumeOn being 1/0
                    MRGlobals.tuningInt = int(split_last[0])
                    MRGlobals.volumeInt = int(split_last[1])
                    # When too low, the volume does jump a bit up and down, resulting in a poor listening experience. Using the
                    #  volume floor allows for improved stability down low.
                    if (MRGlobals.volumeInt <= MRGlobals.volumeFloor):
                        MRGlobals.volumeInt = MRGlobals.volumeFloor
                    MRGlobals.volumeOn = bool(int(split_last[2]))
                except(ValueError, IndexError):
                    # These are expected with some malformed serial stuff, just ignore it.
                    continue
                time.sleep(MRGlobals.clockSleep)
