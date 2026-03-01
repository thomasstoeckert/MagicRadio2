import board
import time
from gpiozero import RotaryEncoder
from signal import pause
import time

pin_a = 5
pin_b = 6

encoder = RotaryEncoder(pin_a, pin_b, wrap=True, max_steps=0)

def on_change():
    print(f"Encoder value: {encoder.steps}")

encoder.when_rotated = on_change

print("Ready!")

pause()