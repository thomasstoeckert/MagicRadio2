from tinytag import TinyTag
import MRGlobals
import Station
import logging
import json
import time
import math
import sys
import os

# A freqPoint is just a small class, holding the station and volume for a single point.
#  the station object can be anything, but it is traditionally an object from the Station
#  module.
class freqPoint:
    def __init__(self, station, volume):
        self.station = station
        self.volume = volume
    def __str__(self):
        return "Station: %s, Volume: %s" % (self.station, self.volume)

"""
    fictTuner handles the creation of the tuning spectrum, begins the initialization of all stations, 
     and generates the points used on the spectrum
"""

class fictTuner:

    # Used as a hard limit, can be changed if there's more wiggle room than expected
    maxStations = 18
    
    # These three are used for the definition of station frequencies, all as radiuses. 
    # loadBuffer is how far out the audio loads silently. Meant to alleviate hitching, implemented back when I used MP3s. 
    # I may eliminate this now that I use oggs.
    loadBuffer = 2
    # dropoffRange is the length of points during which audio clears up or gets more staticy. 
    dropoffRange = 12
    # safeRadius is the length of points durinch which audio is completely clear. 
    safeRadius = 8
    
    # readStationData handles the reading of stations.json, and saves this info in self for buildStations to read
    def readStationData(self):
        # Read station data and stuff here
        stationDataFile = open(MRGlobals.stationsJsonPath)
        self.stationFileData = None
        try:
            self.stationFileData = json.load(stationDataFile)
        except (IOError):
            logging.critical("Station.json not found")
        except (ValueError):
            logging.error("Improper station.json")
        # The program literally cannot run properly without readStationData, so it dies if it doesn't have it.
        assert(self.stationFileData is not None), ("Error in readStationData, shutting down")
        logging.info("Station.json has been found and read properly")
    
    # This goes through all of the stationFileData to build the station objects needed for buildPoints().
    def buildStations(self):
        # Build stations here
        self.stations = []
        for stationData in self.stationFileData:
            newStation = Station.buildStation(stationData)
            # Sometimes it's not quite implemented, this prevents runtime errors
            if newStation is not None:
                self.stations.append(newStation)

        logging.info("Stations have been built")

    # BuildPoints loops through the whole tuning spectrum to generate a frequency point for each possible position of the tuner
    def buildPoints(self):
        # Generate an empty spectrum, 1024 in length to match the possibility of the tuner
        self.points = [freqPoint(Station.StaticStation(), 0)] * 1024

        """
            BuildPoints is done in this pattern/algorithm:
             - Seperate spectrum into the neccesary slices, place stations on the slice lines
             - Iterate through stations beginnings, inserting the rest of the points required for the station
               - loadBuffer -> dropoff -> saveZone -> dropoff -> loadBuffer
        """

        # Cutting the spectrum
        numStations = len(self.stations)
        # The algorithm splits the total frequencies (0-1023) by the number of stations plus one. 
        #  The addition of one allows wiggle room at the top and bottom of the spectrum.
        frequencySplits = 1023 / (numStations + 1)

        # Using the pie slice number to find the start of each station. This is the far left, so it is where the safeRadius begins 
        stationStarts = [0] * numStations
        stationTotalRadius = self.safeRadius + self.dropoffRange + self.loadBuffer
        for index in range(numStations):
            # Station start is the split according to the index (turned into 1-based instead of 0-based) multiplied by the
            #  distance between stations (frequencySplits), minus the radius of the station (for proper centering)
            stationStarts[index] = (frequencySplits * (index + 1) - stationTotalRadius)
        
        # This is the core of the buildPoints function, and it's an ugly monster. I'm sorry.
        for index, stationStart in enumerate(stationStarts):
            # This guy follows us through the process, letting each loop know exactly where to put their data
            currentFreqPoint = stationStart
            currentStation = self.stations[index]

            logging.debug("Building frequency points from %d to %d for %s" % (stationStart, stationStart + stationTotalRadius, currentStation))

            # Points for each station are built through arrays for the different sections of its tuning spectrum
            #  these are later spliced in to prevent massive ugly for-loops. It still doesn't look great, but it's a little better.

            loadBufferPoints = [freqPoint(currentStation, 0.0)] * (self.loadBuffer)

            dropoffPoints = range(self.dropoffRange)
            for dropoffPoint in range(self.dropoffRange):
                # I use an approximation of logarithmic volume, as this makes it operate similar to human hearing, which operates
                #  on a logarithmic scale. My implementation is (x/(dropoffRange))^3. This allows it to scale properly with changing ranges
                pointVolume = math.pow((float(dropoffPoint + 1) / float(self.dropoffRange)), 3)
                dropoffPoints[dropoffPoint] = freqPoint(currentStation, pointVolume)
            
            safePoints = [freqPoint(currentStation, 1.0)] * (self.safeRadius * 2)

            # Apply the slices to the freqPoints list
            # Left-side loadBuffer
            currentFreqPoint = stationStart
            nextFreqPoint = currentFreqPoint + self.loadBuffer
            self.points[currentFreqPoint:nextFreqPoint] = loadBufferPoints
            # Left-side dropoffRange
            currentFreqPoint = nextFreqPoint
            nextFreqPoint = currentFreqPoint + self.dropoffRange
            self.points[currentFreqPoint:nextFreqPoint] = dropoffPoints
            # Central safe zone
            currentFreqPoint = nextFreqPoint
            nextFreqPoint = currentFreqPoint + (self.safeRadius * 2)
            self.points[currentFreqPoint:nextFreqPoint] = safePoints
            # Right-side dropoffRange
            currentFreqPoint = nextFreqPoint
            nextFreqPoint = currentFreqPoint + self.dropoffRange
            self.points[currentFreqPoint:nextFreqPoint] = dropoffPoints[::-1]
            # Right-side loadBuffer
            currentFreqPoint = nextFreqPoint
            nextFreqPoint = currentFreqPoint + self.loadBuffer
            self.points[currentFreqPoint:nextFreqPoint] = loadBufferPoints[::-1]

            logging.debug("Frequency Points created for %s", currentStation)
        
        logging.info("All frequency points created. Total Length: %d", len(self.points))

    # Final assembly of all parts. Organized into seperate functions for cleanliness
    def __init__(self):
        # This takes place over three steps: reading, building stations, and building points
        # Step 1: Reading data from the file
        self.readStationData()
        # Step 2: The longest part, building stations
        self.buildStations()
    
        # Check for station overflow before I build points. This lobs off any extra stations, but it does spit out something in the logs folder.
        numStations = len(self.stations)
        if numStations > self.maxStations:
            self.stations = self.stations[:self.maxStations]
            numStations = self.maxStations
            logging.warn("Too many stations, only took first %d" % self.maxStations)

        # Step 3: Build the spectrum to tune on
        self.buildPoints()

        logging.info("FictionalTuner init completed!")
    
    # Simple function to allow ease-of-access for the point data.
    def getPoint(self, index):
        return self.points[index]