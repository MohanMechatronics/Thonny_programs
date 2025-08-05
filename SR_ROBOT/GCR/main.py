import machine
import utime
import network
import espnow
import struct
import motor


#############################################################
from machine import Pin
import time

boot_button = Pin(0, Pin.IN, Pin.PULL_UP)  # BOOT button
led = machine.Pin(32, machine.Pin.OUT) # For testing the program is running
led.on()

def is_button_hold(threshold_ms=2000):
    start = time.ticks_ms()
    while boot_button.value() == 0:
        if time.ticks_diff(time.ticks_ms(), start) > threshold_ms:
            return True
    return False

###############################################################

robot = motor.car()

station = network.WLAN()
station.active(True)
station.disconnect()

protocol  = espnow.ESPNow()
protocol.active(True)

#important
utime.sleep(0.01)

try:
    while True:
        utime.sleep(0.01)
        host, msg =protocol.recv()
        ax, ay = struct.unpack('ff', msg)

        print("ax = ", ax, "m/s^2  ", " ay = ", ay, "m/s^2")
        
        ########################################################################
        # Check if BOOT button is hold
        if is_button_hold():
            robot.stop()
            led.off() # Make sure the program is stopped
            print("BOOT button held: exiting script")
            utime.sleep(5)
            raise RuntimeError("BOOT button held: exiting script")
        ######################################################################## 
        
        br = 0.4

        if ay>br:
            robot.forward()
        elif ay<-br:
            robot.backward()
        elif ax>br:
            robot.drift_right()
        elif ax<-br:
            robot.drift_left()
        else:
            robot.stop()
    

except OSError as error:
    print("OSError = ", error)
    raise KeyboardInterrupt

except KeyboardInterrupt:
    robot.stop()
    raise SystemExit

except Exception as error:
    robot.stop()
    print("Exception = ", error)
    raise SystemExit