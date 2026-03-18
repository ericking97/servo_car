from time import sleep_ms

from servo_car.components.display import Display
from servo_car.components.drive_train import DriveTrain
from servo_car.components.light import CarLights
from servo_car.components.shift_selector import ShiftSelector
from servo_car.components.uart import UARTController
from servo_car.components.horn import Horn


class Car:
    """
    Composition root that wires together all subsystems of the servo car.

    ``Car`` is the only class that holds reference to every other subsystem.
    Its sole responsability is command dispatch: it reads a UART byte each 
    tick, maps it to the appropiate subsystem action and drives the main 
    loop.
    """
    def __init__(
        self,
        drivetrain: DriveTrain,
        selector: ShiftSelector,
        uart: UARTController,
        horn: Horn,
        car_lights: CarLights,
        display: Display,
    ):
        self._drivetrain = drivetrain
        self._selector = selector
        self._uart = uart
        self._horn = horn
        self._lights = car_lights
        self._display = display
        self._prev_action = None

    def loop(self):
        """
        Start the main control loop. Blocks indefinetely.

        Each iteration of the loop peforms five steps in order:

        1. Reads and dispatch UART command (if one is available)
        2. Poll the drivetrain to advance the speed ramp one tick
        3. Poll the lights to advance one tick
        4. Update the display
        5. Sleep 10ms to yield CPU time and reduce busy-wait overhead.

        The 10ms sleep combined with the drivetrain's 30ms update interval 
        means the ramp advances on roughly every third loop iteration
        """
        print(f"Loop initialized - speed {self._selector.speed}")
        while True:
            self._handle_command(self._uart.read_command())
            self._drivetrain.update()
            self._lights.update()
            self._display.update(
                gear=self._selector.gears.index(self._selector.current) + 1,
                speed=self._selector.speed,
            )
            sleep_ms(10)

    def foward(self):
        """
        Drive both motors forward at the current gear speed.
        """
        speed = self._selector.speed
        self._drivetrain.resync()
        self._drivetrain.set_targets(speed, speed)
        self._lights.forward()

    def backward(self):
        """
        Drive both motors backwards at the current gear speed.
        """
        speed = self._selector.speed
        self._drivetrain.resync()
        self._drivetrain.set_targets(-speed, -speed)
        self._lights.reverse()

    def stop(self):
        """
        Halts the car by setting their target speed to zero
        """
        self._drivetrain.resync()
        self._drivetrain.set_targets(
            left=0,
            right=0,
        )
        self._lights.stop()

    def soft_left(self):
        """
        Arc left by slowing the left motor to half speed.
        The right motor runs at full gear speed while the left runs at 
        half speed, producing a gradual leftward curve rather than a sharp 
        pivot
        """
        speed = self._selector.speed
        self._drivetrain.set_targets(
            left=speed // 2,
            right=speed,
        )
        self._lights.indicate_left()

    def soft_right(self):
        """
        Arc right by slowing the right motor to half speed.
        The left motor runs at full gear speed while the right runs at 
        half speed, producing a gradual rightward curve rather than a sharp 
        pivot
        """
        speed = self._selector.speed
        self._drivetrain.set_targets(
            left=speed,
            right=speed // 2,
        )
        self._lights.indicate_right()

    def sharp_left(self):
        """
        Pivot left by driving the motors in opposite directions at equal 
        full gear speed
        """
        speed = self._selector.speed
        self._drivetrain.set_targets(
            left=-speed,
            right=speed,
        )
        self._lights.party()

    def sharp_right(self):
        """
        Pivot right by driving the motors in opposite directions at equal 
        full gear speed
        """
        speed = self._selector.speed
        self._drivetrain.set_targets(
            left=speed,
            right=-speed,
        )
        self._lights.party()

    def shift_up(self):
        """
        Advance to the next gear.
        """
        try:
            self._selector.shift_up()
            if self._prev_action:
                self._prev_action()
        except ValueError:
            pass

    def shift_down(self):
        """
        Retreat to the lower gear.
        """
        try:
            self._selector.shift_down()
            if self._prev_action:
                self._prev_action()
        except ValueError:
            pass

    def _handle_command(self, command: str | None):
        """
        Dispatch a decoded UART command to the appropiate subsytem action.

        Unknown commands are silently ignored.

        :param command: A single lowercase character
        """
        if command is None:
            return

        actions = {
            "w": self.foward,
            "s": self.backward,
            "a": self.soft_left,
            "d": self.soft_right,
            "q": self.sharp_left,
            "e": self.sharp_right,
            "x": self.stop,
            "f": self._horn.honk,
            "j": self.shift_down,
            "k": self.shift_up,
        }

        action = actions.get(command, None)
        if action:
            if command not in ("j", "k", "f"):
                self._prev_action = action
            action()
