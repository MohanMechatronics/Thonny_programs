from machine import PWM, Pin, time_pulse_us
from time import sleep, sleep_us
from network import WLAN
import socket
from rmc import RMC
import sys
from _thread import start_new_thread
import random, joystick
import urequests

trig, echo = Pin(13, Pin.OUT), Pin(14, Pin.IN)
def read():
    trig.off()
    sleep_us(2)
    trig.on()
    sleep_us(10)
    trig.off()
    dur = time_pulse_us(echo, 1, 30000)
    return int(dur / 58.2) if dur != -1 else 0
pwm = PWM(Pin(15), freq=50)
set_angle = lambda a: pwm.duty_ns(500000 + min(180, max(0, a)) * 11111)
set_angle(90)

robot = RMC()
webpage = joystick.page()
try:
    wifi = WLAN()
    wifi.active(True)
    wifi.connect(b'Chitti', "12345678")
#     wifi.connect(b'Chitti\xc2\xa0CDT', "LMES@123")
    while not wifi.isconnected(): sleep(1)
    ip = wifi.ifconfig()[0]
    print(f'Connected on http://{ip}')
    conn = socket.socket()
    conn.bind((ip, 80))
    conn.listen(1)
    
    THINGSPEAK_WRITE_API_KEY = 'G2B2NEVBCV4D3XNJ'
    THINGSPEAK_CHANNEL_ID = '2906389'

    ip_parts = ip.split(".")

    def send_ip_to_thingspeak(ip_parts):
        url = (f"http://api.thingspeak.com/update?api_key={THINGSPEAK_WRITE_API_KEY}"
               f"&field1={ip_parts[0]}&field2={ip_parts[1]}&field3={ip_parts[2]}&field4={ip_parts[3]}")
        try:
            response = urequests.get(url)
            if response.status_code == 200:
                print("IP Address parts sent to ThingSpeak successfully!")
            else:
                print("Failed to send data to ThingSpeak. Status code:", response.status_code)
            response.close()
        except Exception as e:
            print("Error sending data to ThingSpeak:", e)

    send_ip_to_thingspeak(ip_parts)

    def oar():
        while True:
            dis = read()
            if dis < 15 and (move == "forward" or move == "forward_left" or move == "forward_right"):
                robot.stop()
            else:
                if move == "forward":
                    robot.forward(speed)
                elif move == "forward_left":
                    robot.forward_left(speed)
                elif move == "forward_right":
                    robot.forward_right(speed)
            sleep(0.02)
    start_new_thread(oar,())
    speed = 65535
    move = ""
    while True:
        client, _ = conn.accept()
        request = client.recv(1024).decode()
        request = request.split()[1]
        print(request)
        
        # Direction control
        if request == '/forward?':
            move = "forward"
            action = robot.forward(speed)
        elif request =='/left?':
            move = "left"
            action = robot.drift_left(speed)
        elif request =='/stop?':
            move = "stop"
            action = robot.stop()         
        elif request =='/right?':
            move = "right"
            action = robot.drift_right(speed)
        elif request =='/back?':
            move = "backward"
            action = robot.backward(speed)
        elif request == '/forward_left?':
            move = "forward_left"
            action = robot.forward_left(speed)
        elif request == '/backward_left?':
            action = robot.backward_left(speed)
            move="backward_left"
        elif request == '/forward_right?':
            move = "forward_right"
            action = robot.forward_right(speed)
        elif request == '/backward_right?':
            move="backward_right"
            action = robot.backward_right(speed)          
        elif '/set?speed=' in request:
            speed_str = request.split('/set?speed=')[1]
            speed = round(int(speed_str)*655.35)
            robot.set_speed(speed)         

        if '/set?angle=' in request:
            print(request.split('/set?angle='))
            angle_str = request.split('/set?angle=')[1]
            set_angle(int(angle_str))
            
        response = 'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n' + webpage
        client.sendall(response)
        client.close()            # continuous multi req a handle panrathukaha
        sleep(0.02)
except OSError as err:
    print(err)
    robot.stop()
    sys.exit()
except Exception as err:
    print(err)
    robot.stop()
    sys.exit()
except KeyboardInterrupt:
    robot.stop()
    sys.exit()
