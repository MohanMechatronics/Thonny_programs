from machine import Pin, I2C
import time

# Initialize I2C on custom pins
i2c = I2C(scl=Pin(19), sda=Pin(20), freq=400000)

print("Scanning I2C bus...")

devices = i2c.scan()

if not devices:
    print("No I2C devices found")
else:
    print("I2C devices found:", len(devices))
    for device in devices:
        print("Device address:", hex(device))
