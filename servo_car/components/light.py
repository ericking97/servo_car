from time import sleep_ms
from machine import Pin


class Light:
    """
    Controls a LED light via a single GPIO Pin.
    """

    def __init__(self, pin: Pin):
        """
        Initialise the ping with its GPIO pin.

        :param pin: Pin instance configured as ``Pin.OUT``
        """
        pin.value(0)
        self._pin = pin

    def on(self):
        self._pin.value(1)

    def off(self):
        self._pin.value(0)

    def toggle(self):
        """Toggles the pin signal"""
        self._pin.value(not self._pin.value())

    def blink(self, times: int = 3):
        current = self._pin.value()
        for _ in range(times):
            self.on()
            sleep_ms(500)
            self.off()
            sleep_ms(500)
        self._pin.value(current)


class Lights:
    def __init__(self, left: Light, right: Light):
        self._left = left
        self._right = right

    def on(self):
        self._left.on()
        self._right.on()

    def off(self):
        self._left.off()
        self._right.off()

    def toggle(self):
        self._left.toggle()
        self._right.toggle()

    def turn_right(self):
        self._left.on()
        self._right.blink(5)

    def turn_left(self):
        self._left.blink(5)
        self._right.on()

    def blink(self, times: int = 3):
        self._left.blink(times)
        self._right.blink(times)
