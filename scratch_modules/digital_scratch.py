from gpiozero import Button
from signal import pause

button = Button(4, bounce_time=0.05)

def on_button_press():
    print(f"Volume state: {button.value}!")

button.when_activated = on_button_press
button.when_deactivated = on_button_press

pause()
