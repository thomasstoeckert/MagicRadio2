import busio
import board
import time
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15

# Create I2C bus on default pins
i2c = busio.I2C(board.SCL, board.SDA)

# Create ADS object
ads:ADS1115 = ADS1115(i2c)

# Analog data coming from pin A0
chan = AnalogIn(ads, ads1x15.Pin.A0)

# Rolling filter
window_size = 4
past_data = [0.0] * window_size
w_idx = 0

min_value = 1
max_value = 0x8000

while True:
    chan_rawv = chan.value

    clamp_value = min_value if chan_rawv < min_value else chan_rawv
    clamp_value = max_value if chan_rawv > max_value else chan_rawv

    past_data[w_idx] = clamp_value
    w_idx += 1
    if(w_idx >= window_size): w_idx = w_idx % window_size
    avg = sum(past_data) / window_size

    # ADS has 16-bit input - divide it by max 16-bit value then multiply back to 100%
    print(f"RAW: {chan_rawv: 5d}, AVG: {avg: 5.2f}, NORM: {avg / max_value * 100.0: 3.2f}%")
    
    time.sleep(0.05)
