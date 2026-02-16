from time import sleep
import adafruit_pixelbuf
import board

from adafruit_raspberry_pi5_neopixel_write import neopixel_write

class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

pin = board.D13

pixels = Pi5Pixelbuf(pin, 3, auto_write=True, byteorder="GRB", brightness=0.5)

wheel = [
    0xFF0000,
    0x00FF00,
    0x0000FF,
    0x000000,
]

idx = 0

while True:
    pixels.brightness = (idx % 20) / 20
    pixels.fill(wheel[idx % 4])
    pixels.show()
    idx += 1
    print(f"idx: {idx}")
    sleep(1)