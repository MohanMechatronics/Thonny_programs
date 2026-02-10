import machine
import utime
import motor
import neck
import ultra

boot_button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)  # BOOT button
led = machine.Pin(2, machine.Pin.OUT) # For testing the program is running
led.on()

robot = motor.car()
sensor = ultra.sensor()
servo = neck.servo()

right_dis = 0
left_dis = 0

def is_button_hold(threshold_ms=2000):
    start = utime.ticks_ms()
    while boot_button.value() == 0:
        if utime.ticks_diff(utime.ticks_ms(), start) > threshold_ms:
            return True
    return False

def search():
    global right_dis
    global left_dis
    
    servo.angle(90)
    utime.sleep(0.5)

    servo.angle(50)
    right_dis = sensor.distance()
    print("Right side = ",right_dis)
    utime.sleep(0.5)

    servo.angle(130)
    left_dis = sensor.distance()
    print("Left side = ", left_dis)
    utime.sleep(0.5)

    servo.angle(90)
    utime.sleep(0.5)

# important line
utime.sleep(0.5)

try:
    while True:
        utime.sleep(0.01)
        distance = sensor.distance()

        if distance>35:
            robot.forward()
            print(distance, " cm Go forward")
            
        else:
            robot.stop()
            print(distance, " cm stop")
            search()
            utime.sleep(0.5)
            
            if right_dis>left_dis:
                robot.drift_right()
                utime.sleep(0.6)
                robot.stop()
            
            if right_dis<left_dis:
                robot.drift_left()
                utime.sleep(0.6)
                robot.stop()
        
        # Check if BOOT button is hold
        if is_button_hold():
            robot.stop()
            led.off() # Make sure the program is stopped
            print("BOOT button held: exiting script")
            utime.sleep(5)
            raise SystemExit
        
except OSError as err:
    print("OS error:", err)
    raise KeyboardInterrupt

except KeyboardInterrupt:
    robot.stop()
    print("KeyboardInterrupt detected, stopping robot.")
    raise SystemExit

except Exception as error:
    print(error)
    robot.stop()
    raise SystemExit