from machine import Pin
from time import sleep_ms


class Horn:
    """
    Controls a piezo buzzer horn via a single GPIO pin.

    Attributes:
        _pin (Pin): GPIO ping connected to the horn or buzzer.

    Example:
        >>> horn = Horn(Pin(15, Pin.OUT))
        >>> horn.honk()
    """
    _pin: Pin

    def __init__(self, pin: Pin):
        """
        Initialise the horn with its GPIO pin.

        :param pin: Pin instance configured as ``Pin.OUT``
        """
        self._pin = pin

    def honk(self):
        """
        Sounds the horn.
        """
        self._pin.value(1)
        sleep_ms(150)
        self._pin.value(0)
        sleep_ms(80)
        self._pin.value(1)
        sleep_ms(150)
        self._pin.value(0)
