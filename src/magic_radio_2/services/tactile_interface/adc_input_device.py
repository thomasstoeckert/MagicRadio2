from gpiozero import PolledInternalDevice
from gpiozero.mixins import GPIOQueue
from adafruit_ads1x15 import AnalogIn
from statistics import median
from threading import Event
from time import time

class AnalogDeviceWrapper:
    _analog_device:AnalogIn

    def __init__(self, analog_in:AnalogIn):
        self._analog_device = analog_in
    
    def _read(self):
        return self._analog_device.value
    
class AnalogInputQueueDevice(GPIOQueue):
    _analog_wrapper:AnalogDeviceWrapper

    _last_avg:float = None
    _avg_threshold:float = 20.0
    breached_threshold_event:Event

    def __init__(self, analog_in:AnalogIn):
        self._analog_wrapper = AnalogDeviceWrapper(analog_in)
        self.breached_threshold_event = Event()
        super().__init__(parent=self._analog_wrapper, sample_wait=0.01)
        self.parent = self._analog_wrapper
    
    def _fire_threshold_breached(self):
        if self.when_breached:
            self.when_breached()
    
    def fill(self):
        try:
            while not self.stopping.wait(self.sample_wait):
                value = self.parent._read()
                if value not in self.ignore:
                    self.queue.append(value)
                if not self.full.is_set() and len(self.queue) >= self.queue.maxlen:
                    self.full.set()

                if self.full.is_set() or self.partial:
                    last_average = self._last_avg
                    if(last_average is None): last_average = 1e9
                    new_average = self.value
                    delta_average = abs(new_average - last_average)
                    if(delta_average > self._avg_threshold):
                        self._fire_threshold_breached()
                        self._last_avg = new_average

        except ReferenceError:
            pass


class AnalogInInputDevice(PolledInternalDevice):

    _analog_in_device:AnalogIn = None
    _last_value = None
    _threshold:int = 20

    _queue = None

    def __init__(self, analog_in:AnalogIn, *, threshold:int = 20, event_delay=1.0 / 60.0):
        self._analog_in_device = analog_in
        # self._threshold = threshold
        super().__init__(event_delay=event_delay, pin_factory=None)
        try:
            self._queue = AnalogInputQueueDevice(self._analog_in_device)
            self._queue.start()
            self._threshold = float(threshold)
        except:
            self.close()
            raise
    
    @property
    def value(self):
        return self._queue.value