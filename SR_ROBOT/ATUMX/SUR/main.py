from network import WLAN, AP_IF
import socket
import motor, machine
import sys
import utime

robot=motor.car()
wifi=WLAN(AP_IF)
wifi.active(True)
try:
    wifi.config(essid="Chitti", password="esp@1234", authmode=3)
except OSError:
    pass
while not wifi.active():
    print("Waiting for AP to start...")

print("AP started. IP:", wifi.ifconfig()[0])
ip=wifi.ifconfig()[0]

# Known ESP32-CAM IP
CAM_IP = "192.168.4.5"

boot_button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)  # BOOT button
led = machine.Pin(16, machine.Pin.OUT) # For testing the program is running
led.on()

def is_button_hold(threshold_ms=2000):
    start = utime.ticks_ms()
    while boot_button.value() == 0:
        if utime.ticks_diff(utime.ticks_ms(), start) > threshold_ms:
            return True
    return False

#TCP Protocol
try:
    server=socket.socket()
    server.bind((ip,80))
    server.listen(True)
    while True:
        
        joystick="""<!DOCTYPE html>
                    <html>
                    <head><title>Joystick</title></head>
                    <body>
                    <center>
                    <form action="./forward"><input type="submit" value="Forward" style="height:100px; width:100px"/></form>
                    <table><tr>
                    <td><form action="./left"><input type="submit" value="Left" style="height:100px; width:100px"/></form></td>
                    <td><form action="./stop"><input type="submit" value="Stop" style="height:100px; width:100px"/></form></td>
                    <td><form action="./right"><input type="submit" value="Right" style="height:100px; width:100px"/></form></td>
                    </tr></table>
                    <form action="./back"><input type="submit" value="Back" style="height:100px; width:100px"/></form>
                    </center>
                    </body>
                    </html>"""
        client,address=server.accept()
        request=client.recv(1024)
        request=request.split()[1]
        print(request)
        if request==b'/forward?':
            robot.forward()
        elif request==b'/back?':
            robot.backward()
        elif request==b'/left?':
            robot.drift_left()
        elif request==b'/right?':
            robot.drift_right()
        elif request==b'/stop?':
            robot.stop()
        
        client.send(joystick)
        client.close()
        
        # Check if BOOT button is hold
        if is_button_hold():
            robot.stop()
            led.off() # Make sure the program is stopped
            print("BOOT button held: exiting script")
            utime.sleep(5)
            raise SystemExit

except OSError as err:
    pass

except KeyboardInterrupt:
    robot.stop()
    print("KeyboardInterrupt detected, stopping robot.")
    raise SystemExit

except Exception as error:
    print(error)
    robot.stop()
    raise SystemExit