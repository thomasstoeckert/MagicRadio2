import Segment

"""
    DJ objects take in the 'format' block of a .dj file (special ending, it's really just a json file)
     It then passes that block down to the segment module, part by part, to build a show. When called upon,
     it loops through the segments and has them generate the show. It then pieces it together to give to 
     whatever called it, typically a dynamic station
"""

class DJ:
    # WorkingDir is the full station folder path, relative to the main directory. 
    # djFormatDict is the formatted dictionary containing everything in the "format" block of the .dj file
    def __init__(self, workingDir, djFormatDict):
        self.workingDir = workingDir + "dj/"
        self.show = []
        for segment in djFormatDict:
            builtSegment = Segment.buildSegment(self.workingDir, segment)
            self.show.append(builtSegment)
    
    # This returns the generated show as a list of dictionaries
    #  [{"track": track path, "duration": duration}, {"track": track path, "duration": duration}, ...]
    # Track path is the path to the file from the main operating directory, i.e. "stations/exampleDynamicStation/dj/intros/intro1.ogg"
    # Duration is a float, representing the length of the song in seconds
    def generateShow(self):
        generatedShow = []
        for segment in self.show:
            generatedTracks = segment.generateTrack()
            if generatedTracks is None:
                continue
            generatedShow += generatedTracks
        return generatedShow