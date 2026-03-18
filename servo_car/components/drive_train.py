from time import ticks_ms, ticks_diff

from servo_car.components.motor import Motor

ACCEL_STEP = 1_200
INTERVAL_MS = 30


class DriveTrain:
    """
    Manages smooth acceleration for a two-motor differential drive system.

    Rather that jumping instantly to a target speed, the drive train ramps 
    the current speed toward the targed by a fixed step on each timed update.

    This produces a gradual acceleration and deceleration effect that feels 
    more realistic and protects the hardware from abrupt load changes.

    Speed values are singed integers in the range ``-65,535`` to ``65,535``:
    positive values drive the motor forward, negative values drive it 
    backward and zero stops it.
    """

    def __init__(
        self,
        left: Motor,
        right: Motor,
        accel_step: int = ACCEL_STEP,
        interval_ms: int = INTERVAL_MS,
    ):
        """
        Initialise the drivetrain with two motors and ramp parameters.
        Both motors start with a current and target speed of zero.

        :param left: Motor instance wired to the left motor
        :param right: Motor instance wired to the right motor
        :param accel_step: PWM units to advance toward the target per tick
            update. Defaults to ACCEL_STEP
        :param interval_ms: Minimum time in milliseconds between ramp ticks.
            Defaults to INTERVAL_MS.
        """
        self._left = left
        self._right = right
        self._accel_step = accel_step
        self._interval_ms = interval_ms
        self._last_update = ticks_ms()

        self._current_left = 0
        self._current_right = 0
        self._target_left = 0
        self._target_right = 0

    def set_targets(self, left: int, right: int):
        """
        Sets the desired signed speed for each motor

        :param left: Target signed PWM value for the left motor (-65,535 to 65,535)
        :param left: Target signed PWM value for the right motor (-65,535 to 65,535)
        """
        self._target_left = left
        self._target_right = right

    def update(self):
        """
        Advance the current speeds one step toward the targets and apply them.
        """
        now = ticks_ms()
        if ticks_diff(now, self._last_update) < self._interval_ms:
            return
        self._last_update = now

        self._current_left = self._approach(self._current_left, self._target_left)
        self._current_right = self._approach(self._current_right, self._target_right)
        self._apply(self._left, self._current_left)
        self._apply(self._right, self._current_right)

    def resync(self):
        """
        Equalise current speeds before applying a symmetric motion command.

        After an asymmetric manoeuvre (soft turn, sharp turn), the two motors 
        are at different current speeds. If a symmetric command 
        (forward, backward, stop) is issued immediately, the faster motor 
        reaches the new target before the slower one, pushing the car 
        offcentre during the ramp.

        This method snpas both current speeds to the lower of their two
        absolute values, so the next ramp start from a common baseline and 
        both motors arrive at the target together.
        """
        slower = min(abs(self._current_left), abs(self._current_right))
        self._current_left = slower * (1 if self._current_left >= 0 else -1)
        self._current_right = slower * (1 if self._current_right >= 0 else -1)

    def _approach(self, current: int, target: int) -> int:
        """
        Move ``current`` one step toward ``target``, clamping at the target.

        :param current: The current signed speed value.
        :param target: The desired signed speed value to move towards.
        :returns: The updated signed speed, stepped by at most ``_accel_step``
        """
        if current < target:
            return min(current + self._accel_step, target)
        if current > target:
            return max(current - self._accel_step, target)
        return current

    def _apply(self, motor: Motor, signed_speed: int):
        """
        Traslate a signed speed value into a motor direction call.

        :param motor: The Motor instance to drive.
        :param signed_speed: Signed PWM value; negative means reverse direction
        """
        if signed_speed > 0:
            motor.forward(signed_speed)
        elif signed_speed < 0:
            motor.backward(-signed_speed)
        else:
            motor.stop()
