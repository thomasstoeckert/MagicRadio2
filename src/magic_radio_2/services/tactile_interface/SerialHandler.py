"""
    This file handles the initialization of the serial communication between the raspberry pi and arduino.
    Also known as the littlest file
"""
import MRGlobals
import serial

def initSerial():
    arduino = serial.Serial(MRGlobals.serialPath, MRGlobals.serialBaud)
    return arduino