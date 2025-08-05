import machine
import neopixel
import utime

# Configuration
NUM_LEDS = 60
CENTER_LED = 30
DATA_PIN = 3
BRIGHTNESS = 0.6  # Scale from 0 to 1

# Difficulty levels
EASY = 1
MEDIUM = 2
HARD = 3
ON_SPEED = 4
SONIC_SPEED = 5
ROCKET_SPEED = 6
LIGHT_SPEED = 7
MISSION_IMPOSSIBLE = 8

# Globals
difficulty = EASY
won_this_round = False
led_address = 0
playing = True
cycle_ended = True

# Setup LEDs and button
np = neopixel.NeoPixel(machine.Pin(DATA_PIN), NUM_LEDS)
button = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)

# Color utilities
def set_led(index, color):
    r, g, b = color
    np[index] = (int(r * BRIGHTNESS), int(g * BRIGHTNESS), int(b * BRIGHTNESS))

def clear_all():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

def get_time(diff):
    return {
        EASY: 100,
        MEDIUM: 80,
        HARD: 60,
        ON_SPEED: 40,
        SONIC_SPEED: 30,
        ROCKET_SPEED: 20,
        LIGHT_SPEED: 13,
        MISSION_IMPOSSIBLE: 7
    }.get(diff, 100)

def increase_difficulty():
    global difficulty
    if difficulty != MISSION_IMPOSSIBLE and won_this_round:
        difficulty += 1

def flash():
    for _ in range(2):
        for i in range(NUM_LEDS):
            set_led(i, (255, 0, 0))
        np.write()
        utime.sleep_ms(500)

        clear_all()
        utime.sleep_ms(500)

def fadeall():
    for i in range(NUM_LEDS):
        r, g, b = np[i]
        np[i] = (r // 2, g // 2, b // 2)

def cylon():
    for i in reversed(range(NUM_LEDS)):
        set_led(i, (255, 0, 0))
        np.write()
        fadeall()
        utime.sleep_ms(10)
    for i in range(NUM_LEDS):
        set_led(i, (255, 0, 0))
        np.write()
        fadeall()
        utime.sleep_ms(10)

# Main loop
while True:
    if button.value() == 1 and not playing:
        clear_all()
        set_led(CENTER_LED, (255, 0, 0))
        set_led(led_address, (0, 255, 0))
        np.write()

        if cycle_ended:
            diff = abs(CENTER_LED - led_address)
            if diff == 0:
                won_this_round = True
                if difficulty != MISSION_IMPOSSIBLE:
                    for _ in range(2):
                        cylon()
                else:
                    for _ in range(8):
                        cylon()
                    difficulty = EASY
                increase_difficulty()
                won_this_round = False
            else:
                flash()

            cycle_ended = False

        led_address = 0
        utime.sleep_ms(250)

        if button.value() == 0:
            playing = True

    if playing:
        clear_all()
        set_led(CENTER_LED, (255, 0, 0))
        set_led(led_address, (0, 255, 0))
        np.write()

        led_address -= 1
        if led_address < 0:
            led_address = NUM_LEDS - 1

        utime.sleep_ms(get_time(difficulty))

        if button.value() == 1:
            playing = False
            cycle_ended = True
