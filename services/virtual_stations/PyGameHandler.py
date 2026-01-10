from FictionalTuner import fictTuner
from tinytag import TinyTag
import FictionalTuner
import MRGlobals
import threading
import Station
import logging
import pygame
import time

# Simply gets the sample rate from a file as an int
def getSampleRate(audioPath):
    fileInfo = TinyTag.get(audioPath).samplerate
    return int(float(fileInfo))

# This returns the user volume - calculated from the volumeInt
def calculateUserVolume():
    userVolume = float(MRGlobals.volumeInt + 1) / 1024.0
    if (not MRGlobals.volumeOn):
        userVolume = 0.0
    return userVolume


# This guy prepares pygame and begins playback of static audio. 
def initPygame():
    # PyGame operates on a fixed audio sample rate for some reason. The MagicRadio operates at a sampleRate of 48kHz, slightly higher than CD quality
    defaultSampleRate = getSampleRate(MRGlobals.staticPath)
    pygame.mixer.pre_init(frequency=defaultSampleRate)
    pygame.mixer.init()

    # Setup of the static audio, matching to the current volume of the volume knob
    MRGlobals.staticSound = pygame.mixer.Sound(MRGlobals.staticPath)
    staticVolume = calculateUserVolume()
    MRGlobals.staticSound.set_volume(staticVolume) 
    MRGlobals.staticSound.play(-1) # Loop forever

# This is the class for the audio handling thread. It adjusts volume and tuning, both during boot-up and after
class audioLooper(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        logging.info("Audio thread created, initializing fictTuner..")
        self.lastStation = Station.StaticStation()
        self.lastPosition = 0
        self.tuner = None
        self.booted = False

    def run(self):
        logging.info("Audio thread has begun")
        while MRGlobals.running:

            # Handle sound updates during boot sequence. This is ignored after boot is done.
            if MRGlobals.booting:
                MRGlobals.staticSound.set_volume(calculateUserVolume())
                continue
            elif self.booted == False:
                self.booted = True
                # Play the bootSound to let the user know the radio is ready
                bootSound = pygame.mixer.Sound(MRGlobals.bootAudioPath)
                bootSound.set_volume(calculateUserVolume())
                bootSound.play()

            # Get the point for this frequency on the tuner
            frequency = MRGlobals.tuningInt
            freqPoint = self.tuner.getPoint(frequency)
            newStation = freqPoint.station
            newVolume = freqPoint.volume
            
            # If we're switching between different stations, we need to let the new station know
            #  so it can attempt to resume playback at the proper position
            transferring = False
            if newStation != self.lastStation:
                transferring = True
                logging.info("<%s> --> <%s> at %d" % (self.lastStation, newStation, frequency))
                self.lastStation = newStation
            
            # Run the update code for the current station. Stations ONLY handle audio files, volume is controlled externally.
            newStation.update(pygame.mixer, transferring)

            # The volume of the static sound effect is the inverse of the music volume, so their volumes sum to one.
            invVolume = 1.0 - newVolume
            # Master volume is set by the user and their volume knob
            masterVolume = calculateUserVolume()

            # Since I can't seem to find any way to actually set the pygame volume overall, I multiply the 
            #  volume of each effect and master for the same effect
            MRGlobals.staticSound.set_volume(invVolume * masterVolume)
            pygame.mixer.music.set_volume(newVolume * masterVolume)
            # Sleep for whatever the clock delay is
            time.sleep(MRGlobals.clockSleep)
