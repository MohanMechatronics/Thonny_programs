from machine import Pin, PWM
import time

buzzer = PWM(Pin(4))

def ac_turn_on_sound():
    """AC Turn ON - Rising warm startup sound"""
    print("AC Turning ON...")
    
    # Initial click
    buzzer.freq(200)
    buzzer.duty(512)
    time.sleep(0.05)
    buzzer.duty(0)
    time.sleep(0.05)
    
    # Rising hum - motor starting
    for freq in range(100, 800, 20):
        buzzer.freq(freq)
        buzzer.duty(400)
        time.sleep(0.03)
    
    # Stabilize hum
    for _ in range(3):
        buzzer.freq(800)
        buzzer.duty(300)
        time.sleep(0.1)
        buzzer.duty(200)
        time.sleep(0.1)
    
    # Confirmation double beep
    time.sleep(0.1)
    buzzer.freq(1200)
    buzzer.duty(512)
    time.sleep(0.15)
    buzzer.duty(0)
    time.sleep(0.08)
    buzzer.freq(1500)
    buzzer.duty(512)
    time.sleep(0.2)
    buzzer.duty(0)
    
    print("AC is ON!")

def ac_turn_off_sound():
    """AC Turn OFF - Falling wind-down sound"""
    print("AC Turning OFF...")
    
    # Alert double beep
    buzzer.freq(1500)
    buzzer.duty(512)
    time.sleep(0.15)
    buzzer.duty(0)
    time.sleep(0.08)
    buzzer.freq(1200)
    buzzer.duty(512)
    time.sleep(0.15)
    buzzer.duty(0)
    time.sleep(0.1)
    
    # Falling hum - motor slowing
    for freq in range(800, 80, -20):
        buzzer.freq(freq)
        buzzer.duty(300)
        time.sleep(0.03)
    
    # Fade out clicks
    for duty in range(300, 0, -30):
        buzzer.freq(100)
        buzzer.duty(duty)
        time.sleep(0.02)
    
    buzzer.duty(0)
    print("AC is OFF!")

def ac_beep_confirm():
    """Single confirm beep - button press acknowledgement"""
    buzzer.freq(1000)
    buzzer.duty(512)
    time.sleep(0.08)
    buzzer.duty(0)

def ac_error_sound():
    """Error / fault alert sound"""
    print("AC Error!")
    for _ in range(5):
        buzzer.freq(400)
        buzzer.duty(700)
        time.sleep(0.15)
        buzzer.duty(0)
        time.sleep(0.1)

def ac_temp_reached_sound():
    """Target temperature reached - soft gentle chime"""
    print("Target Temp Reached!")
    notes = [1047, 1319, 1568, 2093]  # C6, E6, G6, C7
    for note in notes:
        buzzer.freq(note)
        buzzer.duty(300)
        time.sleep(0.15)
        buzzer.duty(0)
        time.sleep(0.05)

# ─── Demo ───────────────────────────────────────────
while True:
    ac_beep_confirm()
    time.sleep(0.5)
    
    ac_turn_on_sound()
    time.sleep(3)
    
    ac_temp_reached_sound()
    time.sleep(3)
    
    ac_beep_confirm()
    time.sleep(0.5)
    
    ac_turn_off_sound()
    time.sleep(3)