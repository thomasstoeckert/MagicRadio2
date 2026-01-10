#Global Variables file for Magic Radio

# Usage Variables
running = True
booting = True
clockSleep = 0.016
clockTime = 1529790107.954772
djIntersperse = 1.32
logDeathInDays = 3

# Communication Variables
lastLineReceived = ""
volumeInt = 0
volumeFloor = 20
volumeOn = True
tuningInt = 0

# Serial Variables
# Change serial path to match the path of your arduino
serialPath = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_75638303037351306140-if00"
serialBaud = 9600

# File Paths
staticPath = "audio/static.ogg"
bootAudioPath = "audio/radio-boot.ogg"
stationsFolder = "stations/"
stationsJsonPath = stationsFolder + "/stations.json"

# Sound Objects
staticSound = None