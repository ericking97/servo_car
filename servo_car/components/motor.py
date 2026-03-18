from machine import Pin, PWM


class Motor:
    """
    A high-level interface for controlling a DC motor via PWM and two direction pins.

    This class assumes an H-bridge motor driver (e.g. L298N or DRV8833) where
    direction is set by driving IN1/IN2 high or low, and speed is controlled
    by a PWM duty cycle.

    Attributes:
        pwm (PWM): PWM instance connected to the motor driver's speed control pin (ENA/ENB).
        in1 (Pin): GPIO pin connected to the motor driver's IN1 input.
        in2 (Pin): GPIO pin connected to the motor driver's IN2 input.

    Example:
        >>> pwm = PWM(Pin(15), freq=1000)
        >>> motor = Motor(pwm=pwm, in1=Pin(16), in2=Pin(17))
        >>> motor.forward(32768)  # ~50% speed
        >>> motor.stop()
    """

    pwm: PWM
    in1: Pin
    in2: Pin

    def __init__(self, pwm: PWM, in1: Pin, in2: Pin):
        """
        Initialise the motor with its PWM and direction pins.

        :param pwm: A configured PWM instance for speed control.
                    The frequency should be set before passing it in (e.g. 1000 Hz).
        :param in1: GPIO pin connected to IN1 on the motor driver.
        :param in2: GPIO pin connected to IN2 on the motor driver.
        """
        self.pwm = pwm
        self.in1 = in1
        self.in2 = in2

    def forward(self, speed: int):
        """
        Drive the motor forward at the given speed.

        Sets IN1 low and IN2 high to select the forward direction on the
        H-bridge, then applies the requested duty cycle.

        :param speed: PWM duty cycle in the range 0–65535 (16-bit resolution).
                      0 = stopped, 65535 = full speed.
        """
        self.in1.low()
        self.in2.high()
        self.pwm.duty_u16(speed)

    def backward(self, speed: int):
        """
        Drive the motor backward at the given speed.

        Sets IN1 high and IN2 low to reverse the H-bridge direction,
        then applies the requested duty cycle.

        :param speed: PWM duty cycle in the range 0–65535 (16-bit resolution).
                      0 = stopped, 65535 = full speed.
        """
        self.in1.high()
        self.in2.low()
        self.pwm.duty_u16(speed)

    def stop(self):
        """
        Stop the motor by cutting power and clearing direction pins.

        Sets both IN1 and IN2 low and drops the PWM duty cycle to zero,
        resulting in a coast-to-stop (unpowered) rather than an active brake.
        """
        self.in1.low()
        self.in2.low()
        self.pwm.duty_u16(0)
