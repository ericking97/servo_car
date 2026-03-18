from machine import Pin, I2C
from ssd1306 import SSD1306_I2C


class Display:
    """
    Wraps an SSD1306 I2C OLED screen to show the current gear and speed.

    Only redraws when the values actually change, avoiding unnecessary
    I2C writes on every loop tick.

    Attributes:
        _oled (SSD1306_I2C): The underlying display driver.
        _gear (int): Last rendered gear index (1-based).
        _speed (int): Last rendered speed value.
    """

    WIDTH  = 128
    HEIGHT = 64

    def __init__(self, scl_pin: int = 27, sda_pin: int = 26):
        """
        Initialise the display on I2C1 using the given pins.

        :param scl_pin: GPIO pin number for SCL. Defaults to ``27``.
        :param sda_pin: GPIO pin number for SDA. Defaults to ``26``.
        """
        i2c = I2C(1, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400_000)
        self._oled = SSD1306_I2C(self.WIDTH, self.HEIGHT, i2c)
        self._gear = None
        self._speed = None
        self._oled.fill(0)
        self._oled.show()

    def update(self, gear: int, speed: int):
        """
        Redraw the screen only if the gear or speed has changed.

        Displays the gear number large on the left and the raw PWM
        speed value on the right.

        :param gear: Current gear index (1-based).
        :param speed: Current PWM speed value from :class:`ShiftSelector`.
        """
        if gear == self._gear and speed == self._speed:
            return

        self._gear = gear
        self._speed = speed

        self._oled.fill(0)

        self._oled.text("Gear",  0, 0, 1)
        self._oled.text("Speed", 70, 0, 1)

        gear_str = str(gear)
        speed_str = str(speed)

        self._oled.text(gear_str,  0,  20, 1)
        self._oled.text(gear_str,  1,  20, 1)

        self._oled.text(speed_str, 70, 20, 1)
        self._oled.text(speed_str, 71, 20, 1)

        self._oled.show()
