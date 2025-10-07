import machine
import utime

# ==== Variable declaration ====
buzzer = machine.Pin(4, machine.Pin.OUT)
trigger = machine.Pin(1, machine.Pin.OUT)
echo = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_DOWN)

# ==== Main loop ====
while True:
    # Initial time setup
    utime.sleep(1)
    trigger.off()
    utime.sleep_us(2)
    
    trigger.on()
    utime.sleep_us(3)
    trigger.off()

    # Wait for echo start
    while echo.value() == 0:
        send_time = utime.ticks_us()

    # Wait for echo end
    while echo.value() == 1:
        received_time = utime.ticks_us()

    # Calculate distance
    duration = received_time - send_time
    total_distance = 0.0343 * duration
    object_distance = total_distance / 2

    # If-else condition for buzzer
    if object_distance < 35:
        buzzer.on()
        print(object_distance, "cm Danger")
    else:
        buzzer.off()
        print(object_distance, "cm Safe")
