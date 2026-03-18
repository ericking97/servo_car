from machine import Pin, PWM
from servo_car.components.car import Car
from servo_car.components.drive_train import DriveTrain
from servo_car.components.horn import Horn
from servo_car.components.light import CarLights, Light
from servo_car.components.motor import Motor
from servo_car.components.shift_selector import ShiftSelector
from servo_car.components.uart import UARTController
from servo_car.components.display import Display

ACCEL_STEP = 1_200
INTERVAL_MS = 30

def main():
    right_motor = Motor(
        pwm=PWM(Pin(0), freq=1_000),
        in1=Pin(2, Pin.OUT),
        in2=Pin(3, Pin.OUT),
    )

    left_motor = Motor(
        pwm=PWM(Pin(1), freq=1_000),
        in1=Pin(4, Pin.OUT),
        in2=Pin(5, Pin.OUT),
    )

    drivetrain = DriveTrain(
        left=left_motor,
        right=right_motor,
        accel_step=ACCEL_STEP,
        interval_ms=INTERVAL_MS,
    )

    selector = ShiftSelector(
        speeds=[18_000, 32_000, 50_000, 65_535]
    )

    uart = UARTController(
        tx=Pin(16),
        rx=Pin(17),
    )

    horn = Horn(Pin(19, Pin.OUT))

    car_lights = CarLights(
        front_left=Light(Pin(18, Pin.OUT)),
        front_right=Light(Pin(28, Pin.OUT)),
        rear_left=Light(Pin(15, Pin.OUT)),
        rear_right=Light(Pin(14, Pin.OUT)),
    )

    display = Display(scl_pin=27, sda_pin=26)

    car = Car(
        drivetrain=drivetrain,
        selector=selector,
        uart=uart,
        horn=horn,
        car_lights=car_lights,
        display=display,
    )

    car.loop()

if __name__ == "__main__":
    main()
