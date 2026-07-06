import machine, network, espnow, struct, utime, time

# Add delay to allow proper init
time.sleep(1)

# Wi-Fi in station mode
w0 = network.WLAN(network.STA_IF)
w0.active(True)
w0.disconnect()


# ESP-NOW setup
e = espnow.ESPNow()

e.active(True)

def map_range(x, in_min=0, in_max=4095, out_min=1000, out_max=2000):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Servo control pin (only pin 17 is used)
servo_pin = 10 # 14
pwm = machine.PWM(machine.Pin(servo_pin), freq=50)
servo_pin1 =  9 # 47
pwm1 = machine.PWM(machine.Pin(servo_pin1), freq=50)

# Motor control pins (pins 4, 25, 33, and 32)
motor_pwm = machine.PWM(machine.Pin(1), freq=50)
motor_pwm.duty_u16(0)
motor_pwm1 = machine.PWM(machine.Pin(3), freq=50)
motor_pwm1.duty_u16(0)
motor_pwm2 = machine.PWM(machine.Pin(8), freq=50)
motor_pwm2.duty_u16(0)
motor_pwm3 = machine.PWM(machine.Pin(35), freq=50) #35
motor_pwm3.duty_u16(0)

while True:
    utime.sleep(0.05)
    host, msg = e.recv()
    if msg:
        # Unpack values and label them
        elevator, rudder, not_use, trottel ,not_use1,not_use2 = struct.unpack('6H', msg)

        # Control servo with elevator (pin 17 only)
        duty_us = map_range(4095 - elevator)
        pwm.duty_u16(int((duty_us / 20000) * 65535))
        duty_us1 = map_range(4095 - rudder)
        pwm1.duty_u16(int((duty_us1 / 20000) * 65535))
        # Motor speed control only if trottel > 2000
        if trottel > 2000:
            # Scale trottel from 2000–4095 to 0–65535
#             if trottel < 2300:
# 				pwm1.duty_u16(0)
# 				pwm.duty_u16(0)
            scaled_speed = int(((trottel - 2000) / (4095 - 2000)) * 65535)
            motor_pwm.duty_u16(scaled_speed)
            motor_pwm1.duty_u16(scaled_speed)
            motor_pwm2.duty_u16(scaled_speed)
            motor_pwm3.duty_u16(scaled_speed)
        else:
#  			print("1")
            motor_pwm.duty_u16(0)
            motor_pwm1.duty_u16(0)
            motor_pwm2.duty_u16(0)
            motor_pwm3.duty_u16(0)

        # Print individual values with names
        print(f"elevator = {elevator}, rudder= {rudder}, trottel = {trottel}")


