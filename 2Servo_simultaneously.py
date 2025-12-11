import machine
import utime

# Servos on pins (change if needed)
servo1 = machine.PWM(machine.Pin(10), freq=50)
servo2 = machine.PWM(machine.Pin(9), freq=50)

# Speed configuration — increase to make motion faster
# `STEP_DEG` is degrees moved per loop iteration; larger = faster movement

# `DELAY_MS` is pause per loop in milliseconds; smaller = faster movement
STEP_DEG = 5.0
DELAY_MS = 8

def angle_to_us(angle):
	# angle 0-180 -> 500-2500 us
	return 500 + (angle / 180.0) * 2000

def us_to_duty(us, freq=50):
	period = 1000000 // freq
	return int((us / period) * 65535)

# Initial state
position = 0.0
direction = 1

print("Starting servo oscillation on pins 10 and 9")
try:
	while True:
		# Step size in degrees per loop iteration. Controlled by STEP_DEG.
		step = STEP_DEG * direction

		position += step
		if position >= 180:
			position = 180
			direction = -1
		elif position <= 0:
			position = 0
			direction = 1

		us1 = angle_to_us(position)
		duty1 = us_to_duty(us1)
		# servo1 follows position, servo2 is inverse (180 - position)
		inv_position = 180 - position
		us2 = angle_to_us(inv_position)
		duty2 = us_to_duty(us2)
		servo1.duty_u16(duty1)
		servo2.duty_u16(duty2)

		# Delay controls smoothness and overall speed.
		utime.sleep_ms(DELAY_MS)
except Exception as e:
	try:
		servo1.deinit()
		servo2.deinit()
	except:
		pass
	print("Stopped servo oscillation. Reason:", e)

