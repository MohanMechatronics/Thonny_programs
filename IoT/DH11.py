import machine
import dht
import time

# Set GPIO pin (change if needed)
dht_pin = machine.Pin(13)

# Initialize DHT11 sensor
sensor = dht.DHT11(dht_pin)

while True:
    try:
        sensor.measure()  # Read data
        
        temp = sensor.temperature()  # Temperature in °C
        hum = sensor.humidity()      # Humidity in %
        
        print("Temperature: {}°C".format(temp))
        print("Humidity: {}%".format(hum))
        print("----------------------")
        
    except OSError as e:
        print("Sensor error:", e)
    
    time.sleep(2)  # Delay 2 seconds