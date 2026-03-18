from time import ticks_ms, ticks_diff
from machine import Pin


class Light:
    """
    A single non-blocking LED controlled by a GPIO output pin.
    All timed behaviour is driven by :meth:`update`.
    """

    def __init__(self, pin: Pin):
        self._pin = pin
        self._pin.value(0)
        self._blinking = False
        self._on_ms = 500
        self._off_ms = 500
        self._last_toggle = ticks_ms()

    def solid(self):
        """Turn on and cancel any active blink."""
        self._blinking = False
        self._pin.value(1)

    def off(self):
        """Turn off and cancel any active blink."""
        self._blinking = False
        self._pin.value(0)

    def blink(self, on_ms: int = 400, off_ms: int = 400):
        """Schedule an indefinite non-blocking blink. 
        Stopped by :meth:`off` or :meth:`solid`.
        """
        self._blinking = True
        self._on_ms = on_ms
        self._off_ms = off_ms
        self._last_toggle = ticks_ms()
        self._pin.value(1)

    def update(self):
        """Advance the blink state machine. Call every loop tick."""
        if not self._blinking:
            return
        now = ticks_ms()
        interval = self._on_ms if self._pin.value() else self._off_ms
        if ticks_diff(now, self._last_toggle) < interval:
            return
        self._last_toggle = now
        self._pin.value(not self._pin.value())


class CarLights:
    """
    Four lights wired as a real car: front-left, front-right,
    rear-left, rear-right.
    """

    def __init__(
        self, 
        front_left: Light, 
        front_right: Light,
        rear_left: Light, 
        rear_right: Light
    ):
        self.fl = front_left
        self.fr = front_right
        self.rl = rear_left
        self.rr = rear_right

    def _all(self):
        return (self.fl, self.fr, self.rl, self.rr)

    def forward(self):
        """Rear lights solid. Front lights off."""
        self.fl.off()
        self.fr.off()
        self.rl.solid()
        self.rr.solid()

    def reverse(self):
        """All lights blink — reversing warning."""
        for light in self._all():
            light.blink(on_ms=300, off_ms=300)

    def indicate_left(self):
        """Left side blinks, right side off."""
        self.fl.blink()
        self.rl.blink()
        self.fr.off()
        self.rr.off()

    def indicate_right(self):
        """Right side blinks, left side off."""
        self.fr.blink()
        self.rr.blink()
        self.fl.off()
        self.rl.off()

    def party(self):
        """Blinks all the lights"""
        self.fr.blink()
        self.rr.blink()
        self.fl.blink()
        self.rl.blink()

    def stop(self):
        """All lights off."""
        for light in self._all():
            light.off()

    def update(self):
        """Advance all blink state machines. Call every loop tick."""
        for light in self._all():
            light.update()
