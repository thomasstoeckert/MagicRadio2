# Thomas Stoeckert's MagicRadio 2

The MagicRadio 2 is a revisiting (and revitalizing) of the MagicRadio project I completed eight years ago, [the original MagicRadio.](https://github.com/thomasstoeckert/MagicRadio). While it was an incredible learning experiece, and achieved every goal I had set out for it, it's got some rough edges that I want to smooth out in a version 2.

The changes I have planned are as follows:

## Hardware Improvements
1. New radio! I've bought an old, parts-only "portable" radio that looks promising as a shell.
2. New computer! I was running the original MagicRadio on a super early RaspberryPi - I want to say a Gen 1 B+. Super weak. Led to super long boot times.
3. Digital Encoder Tuner Knob! A potentiometer conected to a knob through a string of dental floss was a neat solution back in the day, but it meant that the floss would slip over time and everything fell out of alignment. Not great.
4. Servo-controlled tuning indicator! See above for the original solution, with the dental floss. This means I can drive the tuning indicator however I want, in fun and creative ways!
5. Battery Power! I want to include a battery bank so that I can take this thing places and turn it on. That means I'll have to achieve a super-low-power idle state, but it should be possible.
6. USB-C! Power standards are nice.
7. Lights! I want some RGB LEDs in the tuner to give more character to the radio. Different colors for different modes.
8. No more additional arduino! Everything lives in the one board.

## Software Improvements
1. Audio is normalized automatically. No more super loud Mr. New Vegas.
2. Web interface for configuring radio stations. Using the radio is all diagetic, but configuring it shouldn't require an SSH session.
3. Support for spotify playlists as a radio station. Easiest way to set up a new radio station is just to put a playlist there, so,
4. Improved bluetooth audio support. Should be a separate operation mode, with much better handling of host status
5. Support for identifying bluetooth beacons. I want this thing to know where it is in my house for future show plans.
6. Spotify Speaker setup. I want to cast to this thing.

This'll be a longer project, I think, but I want to do it right, now with my experience in hardware and software.