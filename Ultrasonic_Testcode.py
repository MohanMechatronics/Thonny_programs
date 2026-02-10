from machine import Pin, time_pulse_us
import time

# Pin configuration
TRIG = Pin(26, Pin.OUT)
ECHO = Pin(27, Pin.IN)

def get_distance():
    # Send trigger pulse
    TRIG.off()
    time.sleep_us(2)
    TRIG.on()
    time.sleep_us(10)
    TRIG.off()

    # Measure echo pulse duration
    duration = time_pulse_us(ECHO, 1, 30000)  # timeout 30ms

    # If no object detected
    if duration < 0:
        return None

    # Distance calculation (cm)
    distance = (duration * 0.0343) / 2
    return distance

print("Ultrasonic Sensor Test Started")

while True:
    dist = get_distance()
    if dist:
        print("Distance: {:.2f} cm".format(dist))
    else:
        print("Out of range")

    time.sleep(1)
