from gpiozero import Servo
from time import sleep

myGPIO = 17

min_pulse_width = 0.5 / 1000
max_pulse_width = 2.5 / 1000

servo = Servo(myGPIO, min_pulse_width=min_pulse_width, max_pulse_width=max_pulse_width)

t = 0
while True:
    servo.min()
    sleep(1)
    servo.max()
    sleep(1)