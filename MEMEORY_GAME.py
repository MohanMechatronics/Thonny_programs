from machine import Pin, PWM
import time
import random

# LED pins
LED_RED = Pin(16, Pin.OUT)
LED_GREEN = Pin(20, Pin.OUT)
LED_BLUE = Pin(28, Pin.OUT)
LED_YELLOW = Pin(17, Pin.OUT)

# Button pins (with pull-ups)
BUTTON_RED = Pin(19, Pin.IN, Pin.PULL_UP)
BUTTON_GREEN = Pin(26, Pin.IN, Pin.PULL_UP)
BUTTON_BLUE = Pin(27, Pin.IN, Pin.PULL_UP)
BUTTON_YELLOW = Pin(21, Pin.IN, Pin.PULL_UP)

# Buzzer (single pin on Pico, we’ll use PWM)
BUZZER = PWM(Pin(18))

# Choices
CHOICE_RED = 1
CHOICE_GREEN = 2
CHOICE_BLUE = 4
CHOICE_YELLOW = 8

CHOICE_OFF = 0
CHOICE_NONE = 0

# Game parameters
ROUNDS_TO_WIN = 13
ENTRY_TIME_LIMIT = 3000  # ms

# Game state
gameBoard = []
gameRound = 0

# LED helper
def setLEDs(choice):
    LED_RED.value(1 if (choice & CHOICE_RED) else 0)
    LED_GREEN.value(1 if (choice & CHOICE_GREEN) else 0)
    LED_BLUE.value(1 if (choice & CHOICE_BLUE) else 0)
    LED_YELLOW.value(1 if (choice & CHOICE_YELLOW) else 0)

# Play buzzer tone
def playTone(freq, ms):
    if freq == 0:
        time.sleep_ms(ms)
        return
    BUZZER.freq(freq)
    BUZZER.duty_u16(32768)  # 50% duty
    time.sleep_ms(ms)
    BUZZER.duty_u16(0)  # stop tone

# Map choice to sound
def toner(choice, ms):
    setLEDs(choice)
    if choice == CHOICE_RED:
        playTone(440, ms)
    elif choice == CHOICE_GREEN:
        playTone(880, ms)
    elif choice == CHOICE_BLUE:
        playTone(587, ms)
    elif choice == CHOICE_YELLOW:
        playTone(784, ms)
    setLEDs(CHOICE_OFF)

# Check button
def checkButton():
    if BUTTON_RED.value() == 0: return CHOICE_RED
    if BUTTON_GREEN.value() == 0: return CHOICE_GREEN
    if BUTTON_BLUE.value() == 0: return CHOICE_BLUE
    if BUTTON_YELLOW.value() == 0: return CHOICE_YELLOW
    return CHOICE_NONE

# Wait for button
def wait_for_button():
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < ENTRY_TIME_LIMIT:
        btn = checkButton()
        if btn != CHOICE_NONE:
            toner(btn, 150)
            while checkButton() != CHOICE_NONE:
                pass
            time.sleep_ms(50)
            return btn
    return CHOICE_NONE

# Add new random step
def add_to_moves():
    global gameBoard
    newButton = random.choice([CHOICE_RED, CHOICE_GREEN, CHOICE_BLUE, CHOICE_YELLOW])
    gameBoard.append(newButton)

# Play back moves
def playMoves():
    for move in gameBoard:
        toner(move, 400)
        time.sleep_ms(200)

# Memory game
def play_memory():
    global gameBoard, gameRound
    gameBoard = []
    gameRound = 0
    while gameRound < ROUNDS_TO_WIN:
        add_to_moves()
        gameRound += 1
        playMoves()
        for i in range(len(gameBoard)):
            btn = wait_for_button()
            if btn == CHOICE_NONE or btn != gameBoard[i]:
                return False
        time.sleep(1)
    return True

# Attract mode
def attractMode():
    while True:
        for c in [CHOICE_RED, CHOICE_BLUE, CHOICE_GREEN, CHOICE_YELLOW]:
            setLEDs(c)
            time.sleep_ms(200)
            if checkButton() != CHOICE_NONE:
                return

# Winner animation
def play_winner():
    for _ in range(3):
        setLEDs(CHOICE_GREEN | CHOICE_BLUE)
        playTone(1000, 200)
        setLEDs(CHOICE_RED | CHOICE_YELLOW)
        playTone(1200, 200)

# Loser animation
def play_loser():
    for _ in range(3):
        setLEDs(CHOICE_RED | CHOICE_GREEN)
        playTone(200, 400)
        setLEDs(CHOICE_BLUE | CHOICE_YELLOW)
        playTone(150, 400)

# Main loop
while True:
    attractMode()
    setLEDs(CHOICE_RED | CHOICE_GREEN | CHOICE_BLUE | CHOICE_YELLOW)
    time.sleep(1)
    setLEDs(CHOICE_OFF)
    time.sleep(0.25)

    if play_memory():
        play_winner()
    else:
        play_loser()
