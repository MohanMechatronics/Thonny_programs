import machine
import utime
import motor

led = machine.Pin(27, machine.Pin.OUT)
led.on()

robot = motor.car()

utime.sleep(0.5)

try:
    while True:

        # ===== FORWARD =====
        robot.forward()
        print("Forward")
        utime.sleep(2)
        robot.stop()
        utime.sleep(1)

        # ===== BACKWARD =====
        robot.backward()
        print("Backward")
        utime.sleep(2)
        robot.stop()
        utime.sleep(1)

        # ===== LEFT =====
        robot.drift_left()
        print("Left")
        utime.sleep(1)
        robot.stop()
        utime.sleep(1)

        # ===== RIGHT =====
        robot.drift_right()
        print("Right")
        utime.sleep(1)
        robot.stop()
        utime.sleep(1)

except KeyboardInterrupt:
    robot.stop()
    print("Stopped safely")
