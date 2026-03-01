try:
    # from ..standard_service import StandardService
    from ...definitions.pin_definitions import *
    from ...definitions.tag_definitions import *
except:
    # from src.magic_radio_2.services.standard_service import StandardService
    from src.magic_radio_2.definitions.pin_definitions import *
    from src.magic_radio_2.definitions.tag_definitions import *
from gpiozero import Button

# Tactile interface server
# Exposes:
# - Tuning Value
# - Mode Switch
# - Volume Value
# - Volume on/off (mute)
# Controls:
# - Tuning Display Servo
# - Tuning Display RGB
# Emits:
# - Tuning Value Changed Event
# - Mode Switch Changed Event
# - Volume Changed event
# - Mute Changed Event

CONST_DEBOUNCE_DURATION_S = 0.1

class ServiceTactileInterface:

    #region Input devices
    # Front-face mode switch
    _btn_mode1:Button
    _btn_mode2:Button
    _btn_mode3:Button

    # Tuner Click (unused)
    _btn_tune_click:Button

    # Mute Switch
    _btn_mute:Button
    #endregion

    _callbacks = []

    def start_service(self):
        self._initialize_digital_inputs()


    def stop_service(self):
        pass

    def register_callback(self, function) -> int:
        self._callbacks.append(function)
        return len(self._callbacks) - 1
    
    def deregister_callback(self, function) -> bool:
        try:
            self._callbacks.remove(function)
            return True
        except:
            return False
    
    def _emit_callback(self, tag:str, value:bool):
        print(f"STI: EMIT EVENT {tag} VALUE {value}")
        for callback in self._callbacks:
            callback(tag, value)
    
    def _internal_switch_callback(self, tag:str, switch:Button):
        # Get the state of the switch
        new_value = switch.value
        # Emit it
        self._emit_callback(tag, new_value)
    
    def _init_button(self, pin:int, tag:str):
        print(f"STI: Initializing button {tag} on pin {pin}")
        new_button = Button(pin, bounce_time=CONST_DEBOUNCE_DURATION_S)
        button_callback = (lambda t=tag, b=new_button: self._internal_switch_callback(t, b))
        new_button.when_activated = button_callback
        new_button.when_deactivated = button_callback
        
    def _initialize_digital_inputs(self):
        # Front-face mode switch
        #self._btn_mode1:Button = self._init_button(PIN_BUTTON_MODE_1, TAG_SWITCH_MODE_1)
        #self._btn_mode2:Button = self._init_button(PIN_BUTTON_MODE_2, TAG_SWITCH_MODE_2)
        #self._btn_mode3:Button = self._init_button(PIN_BUTTON_MODE_3, TAG_SWITCH_MODE_3)

        # Tuner Click (unused)
        self._btn_tune_click:Button = self._init_button(PIN_BUTTON_TUNE_CLICK, TAG_BUTTON_TUNE_CLICK)

        # Mute Switch
        self._btn_mute:Button = self._init_button(PIN_BUTTON_MUTE, TAG_SWITCH_MUTE)

if __name__=="__main__":
    from signal import pause
    sti = ServiceTactileInterface()
    sti.start_service()
    pause()