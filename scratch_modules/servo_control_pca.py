
import busio
import board
from adafruit_servokit import ServoKit
import time
import math


# Create I2C bus on default pins
i2c = busio.I2C(board.SCL, board.SDA)

kit = ServoKit(i2c=i2c, channels=16, address=0x40)

s_idxs = [11, 12, 13]

angle = 0.0
velocity = 1.0

now_time = 0.0
deltatime = 1.0 / 60.0

try:
    while True:
        m_v = (math.sin(now_time * 2 * math.pi) + 1) * 90.0
        print(f"t: {now_time:2.2f}, m_v: {m_v:2.2f}")

        for idx in s_idxs:
            kit.servo[idx].angle = m_v
        now_time += deltatime
        time.sleep(deltatime)

except KeyboardInterrupt:
    print("Program stopped")

    # while True:
    #     print(f"Playing around with index {s_idx}")
    #     kit.servo[s_idx].angle = 0
    #     kit.servo
    #     time.sleep(0.5)
    #     kit.servo[s_idx].angle = 90
    #     time.sleep(0.5)
    #     kit.servo[s_idx].angle = 180
    #     time.sleep(0.5)
    #     s_idx += 1
    #     if(s_idx > 15): s_idx = 0