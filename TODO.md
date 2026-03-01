# Stage 1: Initial Proofs of Concept for subprocesses
I need to validate that each part of the MagicRadio2 works on its own. Namely:
## Hardware Validation
- [x] Audio Playback via PyGame on the RPi5 with the Adafruit DAC hat
- [x] Tactile Input directly on the RPi5 for volume, mute, mode switches
    - [x] ~~Digital Input via GPIO pins~~
    - [x] ~~Analog Input via GPIO pins~~
        - [x] RPi5 has no analog GPIO pins / onboard ADC. Use ADS1115 over I2C
    - [x] ~~Rotary Encoder Input via GPIO pins~~
        - [x] Basic rotary encoders I bought had detents. Felt gross.
        - [x] Swapped out with 652-PEC12R-4022F-S0024 zero-detent pushbutton encoders. Buttery smooth.
- [x] Neopixel Lighting Control on the RPi5
- [x] ~~Servo control on the RPi5~~
    - [x] RPi5 software control of servo SUCKS. Jittery, bad timing. Use external PCA/Servokit
    - [x] Cheapo KY66 plastic servos are too loud. Replace with MG90S metal gear servos.
    - [x] Play back curve data from a CSV on a servo
- [ ] GPIO Driven shutdown / reboot
# Stage 2: Implement the main control process
- [ ] Spawn a dummy service
- [ ] Talk to it. Receive comms back.
- [ ] Manage logging
- [ ] Reboot dummy when it dies
# Stage 3: Implement sub-services
1. [ ] Basic Audio Playback subservice
    - Just plays back a single audio file on loop. Used to test:
2. [ ] Tactile Input subservice
    - [ ] Analog input for volume
    - [ ] Digital input for mute
    - [ ] Digital input for mode switching
    - [ ] Light output.
    - [ ] Emitting events for input changes
3. [ ] Audio Modes
    1. [ ] Synthetic Stations
    2. [ ] Spotify Playlists
    3. [ ] Bluetooth Speaker
4. [ ] Web Interface
5. [ ] Beacon Interface