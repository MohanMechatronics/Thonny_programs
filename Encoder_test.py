from machine import Pin
import time

# =========================
# PIN CONFIGURATION
# =========================
ENC_A = Pin(2, Pin.IN, Pin.PULL_UP)   # CLK
ENC_B = Pin(3, Pin.IN, Pin.PULL_UP)   # DT

# =========================
# VARIABLES
# =========================
position = 0
last_A = ENC_A.value()

# =========================
# INTERRUPT FUNCTION
# =========================
def encoder_callback(pin):
    global position, last_A
    
    current_A = ENC_A.value()
    
    # Detect rising edge
    if last_A == 0 and current_A == 1:
        if ENC_B.value() == 0:
            position += 1   # Clockwise
        else:
            position -= 1   # Counter-clockwise
        
        print("Position:", position)
    
    last_A = current_A

# =========================
# ATTACH INTERRUPT
# =========================
ENC_A.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_callback)

# =========================
# MAIN LOOP
# =========================
while True:
    time.sleep(0.1)