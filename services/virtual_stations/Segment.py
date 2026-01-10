from tinytag import TinyTag
import MRGlobals
import logging
import random
import os

"""
    Segment.py contains all the logic regarding the creation of segments, their inintializaiton, and the 
     picking of tracks according to the segment's behavior/type.
    
    For ease of use, buildSegment() is here. Simply plop in the parent directory (typically "stations/[stationName]/dj/"), the 
     segmentDataDictionary (read from the JSON file by the DynamicStation object, passed through the DJ object), and it'll return
     the appropriate Segment Object to suit your needs. If segmentType doesn't fit or doesn't exist, it'll return a blank segment
     with no tracks while logging an error.
    
    Different Segment types are kind-of similar to the basic Station logic, minus the Update() functions. These run once, generating
     and returning their tracks and the track durations in a list of dicts or None. If it's none, that means the segment doesn't wanna
     run that time, and you should respect it. If it has elements, please merge it into whatever parent list of tracks you've got going on. 
     
    Station Types:
     - Segment:
       - This is a dummy object, just logs an error every time it is called to generate a track
     - PickSegment:
       - Very similar to a pick station, where it picks a track at random. This doesn't have the same logic to prevent repeats, but
         repeats should be much less noticable (and likely) with segments
     - CountPickSegment:
       - This is a pick segment that will return between min and max tracks, useful if you want a segment to run more than once but want
         a little bit of variety in your life. This will never pick duplicates, and will even lower the max if there aren't enough tracks
     - ChancePickSegment:
       - This is a pick segment that will only play segmentRarity percent of the time, stored as a float between 1.0 and 0.0. 1.0 is 100%
         of the time. 0.5 is 50% of the time, 0.0 is 0%, etc. Useful if you don't want something to run every time.
     - DynamicSegment:
       - This guy is like a really great dad. He raises all of his children (initialization), tells them to do their homework (generateTrack),
         and puts it all together to show the world (also in generateTrack). Can be nested within each other.
     - DynamicPickSegment:
       - Like a bad dad version of DynamicSegment. Raises all the children, yes, but only showcases the work of one child when asked.
"""

# Parent path is traditionally "stations/[stationDirectory]/dj/", and segmentDataDictionaries can be found in the .dj files of a station
def buildSegment(parentPath, segmentDataDictionary):
    # EVERY station has these, grab them for easy access
    segmentLabel = segmentDataDictionary["segmentLabel"]
    segmentType = segmentDataDictionary["type"]
    
    # Setup dynamic stations, as they don't have dir's like everyone else
    if segmentType == "dynamic":
        segmentChildData = segmentDataDictionary["segments"]
        return DynamicSegment(parentPath, segmentLabel, segmentChildData)
    elif segmentType == "dynamicPick":
        segmentChildData = segmentDataDictionary["segments"]
        return DynamicPickSegment(parentPath, segmentLabel, segmentChildData)
    
    # From now on, each segment will have a directory
    segmentDir = segmentDataDictionary["dir"]
    if segmentType == "pick":
        return PickSegment(parentPath, segmentLabel, segmentDir)
    elif segmentType == "countPick":
        # Very first numbers in buildSegment! As stated in the block at the top, these are whole numbers used for chance
        segmentMin = int(segmentDataDictionary["min"])
        segmentMax = int(segmentDataDictionary["max"])
        return CountPickSegment(parentPath, segmentLabel, segmentDir, segmentMin, segmentMax)
    elif segmentType == "chance":
        # Rarity is a float between 0.0 and 1.0
        segmentRarity = float(segmentDataDictionary["rarity"])
        return ChanceSegment(parentPath, segmentLabel, segmentDir, segmentRarity)
    
    return Segment(parentPath, segmentLabel)


# Default segment object, don't use this except as a parent
class Segment:

    segmentType = "default"

    def __init__(self, parentPath, segmentLabel):
        self.segmentLabel = segmentLabel
        self.fullSegmentPath = parentPath

    def generateTrack(self):
        logging.error("Default Segment object was asked to create a track. This should not occur.")
        return None

# PickSegment Object handles a lot of file stuff so CountPick and Chance don't have to.
class PickSegment(Segment):

    segmentType = "pick"

    def __init__(self, parentPath, segmentLabel, segmentDir):
        Segment.__init__(self, parentPath, segmentLabel)
        self.segmentDir = segmentDir
        self.fullSegmentPath = parentPath + self.segmentDir + "/"
        self.segmentTracks = [self.fullSegmentPath + file for file in os.listdir(self.fullSegmentPath)]

        # DJ Intersperse here is a global variable giving a bit of spacing between segments. This makes it feel more human and less rushed.
        self.segmentTrackDurations = {}
        for segmentTrack in self.segmentTracks:
            self.segmentTrackDurations[segmentTrack] = float(TinyTag.get(segmentTrack).duration) + MRGlobals.djIntersperse

    
    def generateTrack(self):
        # I make a clone of the list so I can shuffle it about without worrying about the real one
        pickableTracks = list(self.segmentTracks)
        random.shuffle(pickableTracks)
        # Making sure to get the duration, that's critical for persistance in a DynamicStation
        chosenTrack = random.choice(pickableTracks)
        chosenTrackDuration = self.segmentTrackDurations[chosenTrack]
        return [{"track": chosenTrack, "duration": chosenTrackDuration}]

# This is like a bunch of PickSegments joined together, smart enough to not duplicate each other
# It's like a SegmentPede
class CountPickSegment(PickSegment):
    
    segmentType = "countPick"

    # Semgent min and max should both be integers by this point thanks to buildSemgent()
    def __init__(self, parentPath, segmentLabel, segmentDir, segmentMin, segmentMax):
        PickSegment.__init__(self, parentPath, segmentLabel, segmentDir)
        self.segmentMin = segmentMin
        self.segmentMax = segmentMax
        # This block makes sure that max isn't longer than the total number of possible tracks
        if self.segmentMax > len(self.segmentTracks):
            self.segmentMax = len(self.segmentTracks)
        # This block takes care of Min being more than Max. Equal is ok. 
        if self.segmentMin > self.segmentMax:
            self.segmentMin = self.segmentMax
    
    # Behaves slightly differently to a pick segment, as this avoids the same track twice in a row
    #  having them twice in a row would be a big deal for this, as it's supposed to be a DJ, not an
    #  idiot robot. Note that it can produce zero tracks if you chose that as a minimum.
    def generateTrack(self):
        occurences = random.randint(self.segmentMin, self.segmentMax)
        generatedTracks = []
        pickableTracks = list(self.segmentTracks)
        random.shuffle(pickableTracks)
        for occurence in range(occurences):
            chosenTrack = random.choice(pickableTracks)
            pickableTracks.remove(chosenTrack)
            chosenTrackDuration = self.segmentTrackDurations[chosenTrack]
            generatedTracks.append({"track": chosenTrack, "duration": chosenTrackDuration})
        return generatedTracks

# Chance Segments have really nothing too advanced in them, just the ability to not do anything, which I find beautiful
class ChanceSegment(PickSegment):

    segmentType = "chance"

    def __init__(self, parentPath, segmentLabel, segmentDir, segmentRarity):
        PickSegment.__init__(self, parentPath, segmentLabel, segmentDir)
        self.segmentRarity = segmentRarity
    
    def generateTrack(self):
        generatedTrack = PickSegment.generateTrack(self)
        if random.random() < self.segmentRarity:
            # Success!
            return generatedTrack
        else:
            return None

# This guy generates all of its given children. On generateTrack, it merges all their work together in order.
class DynamicSegment(Segment):

    segmentType = "dynamic"

    def __init__(self, parentPath, segmentLabel, segmentChildData):
        Segment.__init__(self, parentPath, segmentLabel)
        self.childSegments = []
        for childData in segmentChildData:
            self.childSegments.append(buildSegment(parentPath, childData))
    
    def generateTrack(self):
        generatedTracks = []
        for child in self.childSegments:
            result = child.generateTrack()
            # Work can be none, in the case of Chance and CountPick
            if result is None:
                continue
            generatedTracks += result
        return generatedTracks


# This is just like a DynamicSegment except only one of its children get chosen to generate a track
class DynamicPickSegment(DynamicSegment):

    segmentType = "dynamicPick"

    def __init__(self, parentPath, segmentLabel, segmentChildData):
        DynamicSegment.__init__(self, parentPath, segmentLabel, segmentChildData)

    def generateTrack(self):
        copyChildren = list(self.childSegments)
        random.shuffle(copyChildren)
        theChosenOne = random.choice(copyChildren)
        return theChosenOne.generateTrack()