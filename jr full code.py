from machine import ADC, TouchPad, Pin, PWM
from utime import sleep
from random import randint
import sys

# SWITCH STATE CHECK
s1 = Pin(13, Pin.IN, Pin.PULL_DOWN)
s2 = Pin(16, Pin.IN, Pin.PULL_DOWN)
s3 = Pin(15, Pin.IN, Pin.PULL_DOWN)
s4 = Pin(14, Pin.IN, Pin.PULL_DOWN)
def switch_state():
    return ((s1.value() * 1) + (s2.value() * 2) + (s3.value() * 3) + (s4.value() * 4))

# buzzer and led control
led_b = Pin(17, Pin.OUT)      # board led
buzzer = Pin(26, Pin.OUT)
led_r = Pin(32, Pin.OUT)
led_l = Pin(33, Pin.OUT)
led_pwm_r,led_pwm_l=PWM(Pin(32)),PWM(Pin(33))
led_pwm_r.freq(1000)
led_pwm_l.freq(1000)
def lr_on():
    led_b.on()
    led_r.on()
    led_l.on()
def lr_off():
    led_b.off()
    led_r.off()
    led_l.off()
def breath(num):
    led=PWM(Pin(num))
    led.freq(1000)
    for i in range(0, 65534+1, 1):
        led.duty_u16(i)
        sleep(0.0001)
    for i in range(65534, 0-1, -1):
        led.duty_u16(i)
        sleep(0.0001)
def b_breath():
    breath(17)
def lr_toggle_breath():
    breath(32)
    breath(33)
def inhale():
    for i in range(0, 65535+1, 1):
        led_pwm_r.duty_u16(i)
        led_pwm_l.duty_u16(i)
        sleep(0.0001)
def exhale():
    for i in range(65535, 0-1, -1):
        led_pwm_r.duty_u16(i)
        led_pwm_l.duty_u16(i)
        sleep(0.0001)
def lr_same_breath():    
    inhale()
    sleep(0.5)
    exhale()
    sleep(0.5)
def onoff(pin=None, sec1=1, sec2=1):
    if pin:
        pin.on()
        sleep(sec1)
        pin.off()
        sleep(sec2)
def l_blink():
    for _ in range(2):
        onoff(led_l, 0.5, 0.2)
def r_blink():
    for _ in range(2):
        onoff(led_r, 0.5, 0.2)
def b_blink():    # board led blink
    onoff(led_b, 0.05, 0.02)
def horn(t1=0.75, t2=0.25):
    onoff(buzzer, t1, t2)
def beep(a=1,b=2):
    for _ in range(2):
        horn(a,b)
def same_blink(t=0.1):
    led_r.on()
    led_l.on()
    sleep(t)
    led_r.off()
    led_l.off()
    sleep(t)
def toggle_blink(t=0.1):
    led_r.on()
    led_l.off()
    sleep(t)
    led_r.off()
    led_l.on()
    sleep(t)
def mix_blink(t=0.01,m=5):
    same_blink()
    sleep(m*t)
    toggle_blink()
    sleep(m*t)

# SENSOR READ
# ANALOG SENSOR
touch_l, touch_r = 4,27
s_left, s_middle, s_right = 35,39,36
l = ADC(Pin(s_left))
r = ADC(Pin(s_right))
m = ADC(Pin(s_middle))
t_l = TouchPad(Pin(touch_l))  # left
t_r = TouchPad(Pin(touch_r))  # right
def a_left():
    return l.read()
def a_right():
    return r.read()
def a_middle():
    return m.read()
def a_touch_l():
    return t_l.read()
def a_touch_r():
    return t_r.read()
# DIGITAL SENSOR
l_d = Pin(Pin(s_left), Pin.IN, Pin.PULL_DOWN)
r_d = Pin(Pin(s_right), Pin.IN, Pin.PULL_DOWN)
m_d = Pin(Pin(s_middle), Pin.IN, Pin.PULL_DOWN)
def d_left():
    return l_d.value()
def d_right():
    return r_d.value()
def d_middle():
    return m_d.value()

# RMC
left_f = Pin(18, Pin.OUT)
left_b = Pin(19, Pin.OUT)
right_f = Pin(22, Pin.OUT)
right_b = Pin(23, Pin.OUT)
en_left = PWM(Pin(21))
en_right = PWM(Pin(25))
en_left.duty(1023)
en_right.duty(1023)
def forward():
    print("Forward")
    left_f.on()
    right_f.on()
    left_b.off()
    right_b.off()        
def backward():
    print("Backward")
    left_f.off()
    right_f.off()
    left_b.on()
    right_b.on()
def left():
    print("Left")
    left_f.off()
    right_f.on()
    left_b.off()
    right_b.off()
def right():
    print("Right")
    left_f.on()
    right_f.off()
    left_b.off()
    right_b.off()
def drift_left():
    print("Drift Left")
    left_f.off()
    right_f.on()
    left_b.on()
    right_b.off()
def drift_right():
    print("Drift Right")
    left_f.on()
    right_f.off()
    left_b.off()
    right_b.on()
def stop():
    print("Stop")
    left_f.off()
    right_f.off()
    left_b.off()
    right_b.off()
    
# all off
def all_off():
    buzzer.off()
    led_r.off()
    led_l.off()
    stop()
    print("i stop all in that robot")

# show index
table = [["ROBOT______","S1 S2 S3 S4","__"],
        ["TESTING______", "1 0 0 0","______"],
        ["RANDOM____", "0 1 0 0" ,"______"],
        ["CLAPGO______", "0 0 1 0","1 1 0 0"],
        ["FIRE BACK_____", "0 0 0 1","1 0 1 0"],
        ["OBSTACLE____", "0 1 1 0","1 0 0 1"],
        ["LINE FOLLOW_", "0 1 0 1","1 1 1 0"],
        ["LIGHT FOLLOW", "0 0 1 1","1 1 0 1" ],
        ["TOUCH_______", "1 0 1 1","______"]]
for row in table:
    print('| {:^14} | {:^2} | {:^2} |'.format(*row)) 

# R2
Dance_new = [
    forward,
    backward,
    left,
    right,
    drift_right,
    drift_left,
    stop
]
def random_ro():
    print("i am random movement Robot")
    move = randint(0, len(Dance_new)-1)
    print(move)
    selected_move =  Dance_new[move]
    selected_move()
    print(selected_move())
    sleep(randint(0,2))

# R4
def fire_back():
    print("i am fireback Robot")
    if a_middle() < 700:
        backward()
        beep(0.05,0.02)        
    else:
        stop()

# R5
def obstacle():
    print("i am obstacle Robot")
    if a_middle() > 700 :
        forward()
    else:
        stop()
        sleep(0.1)
        horn()
        direction = ["left", "right", "back + left", "back + right"]
        k = randint(0, 3)
        if direction[k] == "left":
            drift_left()
            sleep(0.5)
        if direction[k] == "right":
            drift_right()
            sleep(0.5)
        if direction[k] == "back + left":
            backward()
            sleep(0.5)
            drift_left()
            sleep(0.5)
        if direction[k] == "back + right":
            backward()
            sleep(0.5)
            drift_right()
            sleep(0.5)

# R6
def line():
    print("i am line Robot")
    if d_left() == 0 and d_right() == 1:
        drift_right()
    if d_left() == 1 and d_right() == 0:
        drift_left()
    if d_left() == 1 and d_right() == 1:
        forward()
    if d_left() == 0 and d_right() == 0:
        stop()

# R7
def light():
    print("i am light Robot")
    if d_left() == 0 and d_right() == 0:
        forward()
    elif d_left() == 0 and d_right() == 1: 
        drift_left()
    elif d_left() == 1 and d_right() == 0:
        drift_right()
    else:
        stop()

# R8
myleft = []
myright = []
ll = None
rr = None
def touch_robot():
#     print(a_touch_l(), a_touch_r(),myleft,myright)
    global ll, rr
    myleft.append(a_touch_l())
    myright.append(a_touch_r())
    if len(myleft) >= 2:
        if max(myleft) - min(myleft) > 50:
            ll = max(myleft)
            myleft.clear()
        else:
            myleft.remove(min(myleft))
    if len(myright) >= 2:
        if max(myright) - min(myright) > 50:
            rr = max(myright)
            myright.clear()
        else:
            myright.remove(min(myright))
    if ll is not None and rr is not None:
        if ll - a_touch_l() > 50 and rr - a_touch_r() > 50:
            forward()
        elif ll - a_touch_l() > 50:
            left()
        elif rr - a_touch_r() > 50:
            right()
        else:
            backward()
    elif rr is not None:
        if rr - a_touch_r() > 50:
            right()
        else:
            backward()
    elif ll is not None:
        if ll - a_touch_l() > 50:
            left()
        else:
            backward()
    else:
        backward()


# integration of robotic functionalities
lr_off()
print(switch_state())
do_once = 1
state = 0
while True:
    try:
        if switch_state() == 0:
            if do_once == 1:
                print("\nwaiting: SELECT THE ROBOT YOU WANT")
                do_once = 0
            all_off()
            sleep(0.2)
            b_breath()
            sleep(0.5)
        elif switch_state() == 1:
            en_left.duty(1023)
            en_right.duty(1023)  
            forward()
            b_blink()
            sleep(0.1)
        elif switch_state() == 2:
            random_ro()
            sleep(0.1)
        elif switch_state() == 3:
#             print("I'm Clap-go robot")
            en_left.duty(768)
            en_right.duty(768)
            previous_state = state
            if d_middle() == 1:    # False
                if previous_state == 0:
                    if state ==0:
                        forward()
                        state = 1
                if previous_state == 1:
                    if state == 1:
                        stop()
                        state = 0
                sleep(0.2)
        elif switch_state() == 4:
            fire_back()
            sleep(0.1)
        elif switch_state() == 5:
            obstacle()
            sleep(0.1)
        elif switch_state() == 6:
            en_left.duty(780)
            en_right.duty(780)
            line()
            sleep(0.01)
        elif switch_state() == 7:
            light()
            sleep(0.1)
        elif switch_state() == 8:
            touch_robot()
            sleep(0.1)
        else:          
            print("no Robot Assigned")            
    except KeyboardInterrupt:
        all_off()
        sys.exit()
    except Exception as e:
        print("error: ",e)
        all_off()
        sys.exit()