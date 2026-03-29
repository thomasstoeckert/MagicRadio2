# from ..standard_service import StandardService
from ...definitions.pin_definitions import *
from ...definitions.tag_definitions import *
from .adc_input_device import AnalogInInputDevice

from gpiozero import Button, RotaryEncoder
import busio
import board
import asyncio
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15
from adafruit_servokit import ServoKit

# Tactile interface server
# Exposes:
# - Tuning Value
# - Mode Switch
# - Volume Value
# - Volume on/off (mute)
# <complete>
#
# Controls:
# - Tuning Display Servo
# - Tuning Display RGB
#
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

    # Tuner Encoder
    _enc_tuner:RotaryEncoder

    # ADS Input
    _ads_board:ADS1115
    _ads_analog_in:AnalogIn
    _ads_rolling_window_size = 4
    _ads_rolling_window:list
    _ads_rolling_idx:int
    _ads_min_value = 1
    _ads_max_value = 0x8000
    _ads_average_value:int

    _ads_enable_service = False
    _ads_polling_service = None
    _ads_polling_rate_ms = 25
    _ads_polling_threshold = 10
    #endregion

    _callbacks = []

    #region Output Devices
    _servo_kit:ServoKit
    _servo = None
    # Per manufacturer's spec - 500us is 0°, 2500us is 180°
    # https://www.amazon.com/dp/B0CP98TZJ2?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1
    _servo_min_pulse_width = 500
    _servo_max_pulse_width = 2500
    #endregion


    def start_service(self):
        # Initialize i2c bus
        i2c_bus = busio.I2C(board.SCL, board.SDA)

        self._initialize_digital_inputs()
        self._initialize_encoder_inputs()
        self._initialize_analog_inputs(i2c_bus)
        self._initialize_servo_output(i2c_bus)

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
    
    def receive_event(self, tag, value):
        if(tag == TAG_SET_SERVO):
            self._servo.angle = value
    
    def _emit_callback(self, tag:str, value:any):
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
    
    def _internal_encoder_callback(self, tag:str, encoder:RotaryEncoder):
        new_value = encoder.value
        self._emit_callback(tag, new_value)

    def _initialize_encoder_inputs(self):
        self._enc_tuner = RotaryEncoder(PIN_ENCODER_TUNE_A, PIN_ENCODER_TUNE_B, wrap=True, max_steps=0)
        self._enc_tuner.when_rotated_clockwise = (lambda t=TAG_ENCODER_TUNE_UP, enc=self._enc_tuner: self._internal_encoder_callback(t, enc))
        self._enc_tuner.when_rotated_counter_clockwise = (lambda t=TAG_ENCODER_TUNE_DOWN, enc=self._enc_tuner: self._internal_encoder_callback(t, enc))
    
    def _initialize_analog_inputs(self, i2c_bus):
        self._ads_board = ADS1115(i2c_bus)
        self._ads_analog_in = AnalogIn(self._ads_board, ads1x15.Pin.A0)
        print("Hello?")

        print(f"Initial analog value: {self._ads_analog_in.value}")
        self._adc_input_device = AnalogInInputDevice(self._ads_analog_in)
        self._adc_input_device._queue.when_breached = (lambda t=TAG_ANALOG_VOLUME_CHANGE: self._emit_callback(t, float(self._adc_input_device.value) / self._ads_max_value * 100.0))
        print("Passed setup")
        # self._adc_input_device.when_activated = (lambda t=TAG_ANALOG_VOLUME_CHANGE: self._emit_callback(t, float(self._adc_input_device.value) / self._ads_max_value * 100.0))

        # # Prepare our window
        # self._ads_average_value = self._ads_analog_in.value
        # self._ads_rolling_window = [self._ads_average_value] * self._ads_rolling_window_size
        # self._ads_rolling_idx = 0
        
        # # Establish the polling method that's going to grab our data
        # self._ads_enable_service = True

        # # Start our polling service
        # self._ads_polling_service = asyncio.run(self._analog_polling_service_task())

    async def _analog_polling_service_task(self):
        while self._ads_enable_service:
            # Sample data from our analog input
            raw_value = self._ads_analog_in.value

            # Clamp our raw value to our allowed min / max values
            clamp_value = self._ads_min_value if raw_value < self._ads_min_value else raw_value
            clamp_value = self._ads_max_value if raw_value > self._ads_max_value else raw_value

            # Place it into our window
            self._ads_rolling_window[self._ads_rolling_idx] = clamp_value
            # Increment our window
            self._ads_rolling_idx += 1
            if(self._ads_rolling_idx >= self._ads_rolling_window_size):
                self._ads_rolling_idx = self._ads_rolling_idx % self._ads_rolling_window_size
            
            # Calculate our new average
            new_average = sum(self._ads_rolling_window) / self._ads_rolling_window_size
            delta_value = abs(new_average - self._ads_average_value)
            if(delta_value > self._ads_polling_threshold):
                self._emit_callback(TAG_ANALOG_VOLUME_CHANGE, new_average)
                self._ads_average_value = new_average

            # Sleep
            await asyncio.sleep(self._ads_polling_rate_ms / 1000)
    
    def _initialize_servo_output(self, i2c_bus):
        self._servo_kit = ServoKit(i2c=i2c_bus, channels=16, address=0x40)
        self._servo = self._servo_kit.servo[PIN_SERVO_INDEX]
        self._servo.set_pulse_width_range(self._servo_min_pulse_width, self._servo_max_pulse_width)
        # Home the servo.
        self._servo.angle = 0.0

if __name__=="__main__":

    sti = ServiceTactileInterface()

    tune_value = 0.0
    tune_multiplier = 2.0
    def move_servo_on_callback(event, value):
        global tune_value
        if(event == TAG_ENCODER_TUNE_UP):
            tune_value += (1.0 * tune_multiplier)

        if(event == TAG_ENCODER_TUNE_DOWN):
            tune_value -= (1.0 * tune_multiplier)
        if(tune_value >= 180.0): tune_value = 179.0
        if(tune_value < 0.0): tune_value = 0.0
        
        if(event == TAG_ENCODER_TUNE_DOWN or event == TAG_ENCODER_TUNE_UP):
            sti.receive_event(TAG_SET_SERVO, tune_value)
    
    sti.register_callback(move_servo_on_callback)

    sti.start_service()
    from signal import pause
    pause()