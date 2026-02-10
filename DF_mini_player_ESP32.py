from machine import UART
import time

# UART2 on ESP32
df = UART(2, baudrate=9600, tx=19, rx=18)

# DFPlayer command sender
def df_send(cmd, param=0):
    packet = bytearray([
        0x7E,       # start
        0xFF,       # version
        0x06,       # length
        cmd,        # command
        0x00,       # no feedback
        (param >> 8) & 0xFF,
        param & 0xFF,
        0xEF        # end
    ])
    df.write(packet)

# --- DFPlayer Commands ---
def set_volume(vol):        # 0–30
    df_send(0x06, vol)

def play_track(num):        # 0001.mp3 → 1
    df_send(0x03, num)

def loop_all():
    df_send(0x11)

# ---- MAIN ----
time.sleep(1)               # allow DFPlayer boot

print("Initializing DFPlayer")

set_volume(30)              # max allowed volume
time.sleep(0.2)

play_track(5)               # plays 0004.mp3
# loop_all()                # uncomment to loop all songs

print("DFPlayer command sent")

while True:
    time.sleep(1)
