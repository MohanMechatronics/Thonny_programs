import machine
import neopixel
import time
import math

# Configuration
LED_PIN = 21
LED_COUNT = 39  # Number of LEDs
np = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)

# Set brightness scale (0.0 to 1.0)
BRIGHTNESS = 0.3

def apply_brightness(color):
    return tuple(int(c * BRIGHTNESS) for c in color)

def color_wipe(color, wait_ms):
    for i in range(LED_COUNT):
        np[i] = apply_brightness(color)
        np.write()
        time.sleep_ms(wait_ms)

def theater_chase(color, wait_ms):
    for a in range(10):
        for b in range(3):
            for i in range(LED_COUNT):
                np[i] = (0, 0, 0)
            for c in range(b, LED_COUNT, 3):
                np[c] = apply_brightness(color)
            np.write()
            time.sleep_ms(wait_ms)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

def rainbow(wait_ms):
    for j in range(256):  # Full cycle of rainbow
        for i in range(LED_COUNT):
            idx = (i * 256 // LED_COUNT + j) & 255
            np[i] = apply_brightness(wheel(idx))
        np.write()
        time.sleep_ms(wait_ms)

def theater_chase_rainbow(wait_ms):
    for j in range(256):
        for q in range(3):
            for i in range(0, LED_COUNT, 1):
                np[i] = (0, 0, 0)
            for i in range(q, LED_COUNT, 3):
                color = wheel((i + j) % 255)
                np[i] = apply_brightness(color)
            np.write()
            time.sleep_ms(wait_ms)

# Main Loop
while True:
    color_wipe((255, 0, 0), 30)     # Red
    color_wipe((0, 255, 0), 30)     # Green
    color_wipe((0, 0, 255), 30)     # Blue

    rainbow(10)
    theater_chase_rainbow(50)
