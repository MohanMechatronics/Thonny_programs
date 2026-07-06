from machine import Pin
from utime import sleep
from servo_lib import Servo
from rfid_lib import RFID

reader = RFID(cs=5, sck=18, mosi=23, miso=19)
door = Servo(25)

authorized_tags = {"0xec7c7c00": "Tamil", "0x69ba7900": "Aakash"}

while True:
    sleep(1)
    tag = reader.read()
    print(tag)

    if tag in authorized_tags:
        name = authorized_tags[tag]
        print("Door Access:", name)
        
        door.unlock()
        sleep(2)
        door.lock()