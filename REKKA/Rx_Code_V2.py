import machine, network, espnow, struct, utime, time

time.sleep(1)

w0 = network.WLAN(network.STA_IF)
w0.active(True)
w0.disconnect()

e = espnow.ESPNow()
e.active(True)

def map_range(x, in_min=0, in_max=4095, out_min=1000, out_max=2000):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Servo pins
pwm = machine.PWM(machine.Pin(14), freq=50)   # elevator
pwm1 = machine.PWM(machine.Pin(47), freq=50)  # rudder servo

# Motor pins
motor_pwm  = machine.PWM(machine.Pin(1), freq=50)   # LEFT 1
motor_pwm1 = machine.PWM(machine.Pin(3), freq=50)   # LEFT 2
motor_pwm2 = machine.PWM(machine.Pin(8), freq=50)   # RIGHT 1
motor_pwm3 = machine.PWM(machine.Pin(35), freq=50)  # RIGHT 2

while True:
    utime.sleep(0.05)
    host, msg = e.recv()

    if msg:
        elevator, rudder, _, trottel, _, _ = struct.unpack('6H', msg)

        # ----- Servo control -----
        duty_us = map_range(4095 - elevator)
        pwm.duty_u16(int((duty_us / 20000) * 65535))

        duty_us1 = map_range(4095 - rudder)
        pwm1.duty_u16(int((duty_us1 / 20000) * 65535))

        # ----- Motor control -----
        if trottel > 2000:
            base_speed = int(((trottel - 2000) / (4095 - 2000)) * 65535)

            # Rudder center ≈ 2048
            rudder_offset = rudder - 2048
            turn_strength = int((rudder_offset / 2048) * base_speed * 0.5)

            left_speed  = base_speed + turn_strength
            right_speed = base_speed - turn_strength

            # Clamp values
            left_speed  = max(0, min(65535, left_speed))
            right_speed = max(0, min(65535, right_speed))

            # Apply speeds
            motor_pwm.duty_u16(left_speed)
            motor_pwm1.duty_u16(left_speed)
            motor_pwm2.duty_u16(right_speed)
            motor_pwm3.duty_u16(right_speed)
        else:
            motor_pwm.duty_u16(0)
            motor_pwm1.duty_u16(0)
            motor_pwm2.duty_u16(0)
            motor_pwm3.duty_u16(0)

        print(f"elevator={elevator}, rudder={rudder}, throttle={trottel}")
