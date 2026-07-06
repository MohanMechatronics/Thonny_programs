from machine import Pin, SoftI2C
import ssd1306, time, random, math

# ── PINS ──
i2c  = SoftI2C(sda=Pin(20), scl=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
clk  = Pin(2, Pin.IN, Pin.PULL_UP)
dt   = Pin(3, Pin.IN, Pin.PULL_UP)
sw   = Pin(4, Pin.IN, Pin.PULL_UP)

# ── STATES ──
ST_MENU  = 0
ST_VAL   = 1
ST_REACT = 2
ST_SPIN  = 3

state    = ST_MENU
menu_sel = 0
MENU     = ["Encoder Value", "Reaction Game", "Spin Game"]

# ── ENCODER ──
# Two separate counters:
#   position  → used ONLY for ST_VAL display (like standalone code)
#   enc_raw   → used for menu/spin (relative movement)
position  = 0       # absolute, shown on display
enc_raw   = 0       # raw tick counter for menus/games
last_A    = clk.value()
btn_event = False

def encoder_isr(pin):
    global position, enc_raw, last_A
    cur_A = clk.value()
    if last_A == 0 and cur_A == 1:      # rising edge
        if dt.value() == 0:
            position += 1
            enc_raw  += 1
        else:
            position -= 1
            enc_raw  -= 1
    last_A = cur_A

def button_isr(pin):
    global btn_event, position
    time.sleep_ms(30)
    if sw.value() == 0:
        if state == ST_VAL:
            position = 0            # short press = reset in value screen
        else:
            btn_event = True

clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_isr)
sw.irq(trigger=Pin.IRQ_FALLING, handler=button_isr)

# ── REACTION GAME VARS ──
r_best  = 9999
r_phase = "wait"
r_wait  = 0
r_t0    = 0
r_ms    = 0

# ── SPIN GAME VARS ──
sp_angle  = 0
sp_speed  = 12
sp_target = 0
sp_score  = 0

# ─────────────────────────────────────────
def btn_clear():
    global btn_event
    btn_event = False
    while sw.value() == 0:
        time.sleep_ms(10)

def cx(txt, y, col=1):
    oled.text(txt, max(0, (128 - len(txt) * 8) // 2), y, col)

def draw_needle(angle, ox, oy, r):
    rad = math.radians(angle - 90)
    oled.line(ox, oy,
              int(ox + r * math.cos(rad)),
              int(oy + r * math.sin(rad)), 1)

# ─────────────────────────────────────────
def scr_menu():
    oled.fill(0)
    cx("= GAME CONSOLE =", 0)
    oled.hline(0, 10, 128, 1)
    for i, item in enumerate(MENU):
        y = 14 + i * 17
        if i == menu_sel:
            oled.fill_rect(0, y - 1, 128, 13, 1)
            oled.text("> " + item, 4, y, 0)
        else:
            oled.text("  " + item, 4, y)
    oled.show()

# ── Encoder value screen: uses 'position' only ──
def scr_val():
    oled.fill(0)

    oled.text("ENCODER VALUE", 0, 0)
    oled.hline(0, 10, 128, 1)

    # Big centred number
    vs = str(position)
    oled.text(vs, max(0, (128 - len(vs) * 8) // 2), 22)

    # Centre-origin bar
    oled.hline(0, 38, 128, 1)
    oled.vline(64, 35, 6, 1)
    bar = min(63, abs(position))
    if position > 0:
        oled.fill_rect(64, 35, bar, 5, 1)
    elif position < 0:
        oled.fill_rect(64 - bar, 35, bar, 5, 1)

    if position > 0:
        status = ">>> CW"
    elif position < 0:
        status = "CCW <<<"
    else:
        status = "-- ZERO --"
    cx(status, 46)
    cx("Btn=Reset  LongP=Menu", 56)
    oled.show()

def scr_react_wait():
    oled.fill(0)
    cx("REACTION GAME", 0)
    oled.hline(0, 10, 128, 1)
    cx("Get ready...", 20)
    cx("Press when screen", 34)
    cx("turns WHITE!", 44)
    best = "Best: --" if r_best == 9999 else "Best: " + str(r_best) + "ms"
    cx(best, 56)
    oled.show()

def scr_react_go():
    oled.fill(1)
    oled.text("!! PRESS !!", 16, 20, 0)
    oled.text("!!  NOW  !!", 16, 36, 0)
    oled.show()

def scr_react_result():
    oled.fill(0)
    cx("REACTION RESULT", 0)
    oled.hline(0, 10, 128, 1)
    cx(str(r_ms) + " ms", 18)
    if r_ms < 200:   grade = "SUPERHUMAN!!"
    elif r_ms < 300: grade = "Lightning fast"
    elif r_ms < 450: grade = "Great reflexes"
    elif r_ms < 600: grade = "Not bad!"
    else:            grade = "Keep practising"
    cx(grade, 32)
    cx("Best: " + str(r_best) + "ms", 44)
    cx("Btn=again  LongP=menu", 56)
    oled.show()

def scr_react_early():
    oled.fill(0)
    cx("TOO EARLY!", 18)
    cx("Wait for white", 32)
    cx("screen first!", 44)
    oled.show()

def scr_spin():
    oled.fill(0)
    cx("SPIN  STOP", 0)
    oled.hline(0, 10, 128, 1)
    ocx, ocy, r = 32, 40, 20
    for a in range(0, 360, 45):
        rad = math.radians(a - 90)
        x1 = int(ocx + (r - 4) * math.cos(rad))
        y1 = int(ocy + (r - 4) * math.sin(rad))
        x2 = int(ocx + r * math.cos(rad))
        y2 = int(ocy + r * math.sin(rad))
        oled.line(x1, y1, x2, y2, 1)
    trad = math.radians(sp_target - 90)
    tx = int(ocx + (r + 4) * math.cos(trad))
    ty = int(ocy + (r + 4) * math.sin(trad))
    oled.fill_rect(tx - 2, ty - 2, 5, 5, 1)
    draw_needle(sp_angle, ocx, ocy, r - 5)
    oled.fill_rect(ocx - 1, ocy - 1, 3, 3, 1)
    oled.text("Spd:" + str(sp_speed), 70, 14)
    oled.text("Score:", 70, 30)
    oled.text(str(sp_score), 70, 40)
    oled.text("Btn=STOP", 70, 54)
    oled.show()

def scr_spin_result(diff, pts):
    oled.fill(0)
    cx("SPIN RESULT", 0)
    oled.hline(0, 10, 128, 1)
    if diff <= 8:    msg = "BULLS-EYE!!"
    elif diff <= 20: msg = "Excellent!"
    elif diff <= 40: msg = "Close!"
    else:            msg = "Missed..."
    cx(msg, 18)
    cx("Off by " + str(diff) + " deg", 32)
    cx("+" + str(pts) + " pts", 44)
    cx("Score: " + str(sp_score), 54)
    oled.show()

# ─────────────────────────────────────────
#  SPLASH
oled.fill(0)
cx("ESP32-C3", 10)
cx("GAME  CONSOLE", 26)
cx("Turn knob to start", 44)
oled.show()
time.sleep(1)

# Snapshots for relative movement (menu + spin only)
last_menu = enc_raw
last_spin = enc_raw

# ─────────────────────────────────────────
#  MAIN LOOP
while True:

    # ══ MENU ══════════════════════════════
    if state == ST_MENU:
        d = enc_raw - last_menu
        if d:
            menu_sel  = (menu_sel + (1 if d > 0 else -1)) % len(MENU)
            last_menu = enc_raw
        if btn_event:
            btn_clear()
            if menu_sel == 0:
                state = ST_VAL          # enter value screen, position unchanged
            elif menu_sel == 1:
                r_phase = "wait"
                r_wait  = random.randint(2000, 5000)
                r_t0    = time.ticks_ms()
                state   = ST_REACT
            elif menu_sel == 2:
                sp_target = random.randint(0, 359)
                sp_speed  = 12
                sp_angle  = 0
                last_spin = enc_raw
                state     = ST_SPIN
        scr_menu()

    # ══ ENCODER VALUE ═════════════════════
    elif state == ST_VAL:
        scr_val()
        # Long press → back to menu
        if not sw.value():
            t0 = time.ticks_ms()
            while not sw.value(): time.sleep_ms(10)
            if time.ticks_diff(time.ticks_ms(), t0) > 1000:
                btn_event = False
                last_menu = enc_raw     # re-sync menu
                state     = ST_MENU

    # ══ REACTION GAME ═════════════════════
    elif state == ST_REACT:
        now = time.ticks_ms()

        if r_phase == "wait":
            scr_react_wait()
            if btn_event:
                btn_clear()
                r_phase = "early"
                r_t0    = now
            elif time.ticks_diff(now, r_t0) >= r_wait:
                r_phase = "go"
                r_t0    = now

        elif r_phase == "early":
            scr_react_early()
            if btn_event:
                btn_clear()
            if time.ticks_diff(now, r_t0) > 1500:
                r_phase = "wait"
                r_wait  = random.randint(2000, 5000)
                r_t0    = now

        elif r_phase == "go":
            scr_react_go()
            if btn_event:
                btn_clear()
                r_ms = time.ticks_diff(now, r_t0)
                if r_ms < r_best:
                    r_best = r_ms
                r_phase = "result"

        elif r_phase == "result":
            scr_react_result()
            if btn_event:
                btn_clear()
                r_phase = "wait"
                r_wait  = random.randint(2000, 5000)
                r_t0    = time.ticks_ms()

        if not sw.value():
            t0 = time.ticks_ms()
            while not sw.value(): time.sleep_ms(10)
            if time.ticks_diff(time.ticks_ms(), t0) > 1000:
                btn_event = False
                last_menu = enc_raw
                state     = ST_MENU

    # ══ SPIN GAME ═════════════════════════
    elif state == ST_SPIN:
        d = enc_raw - last_spin
        if d:
            sp_speed  = max(1, min(40, sp_speed + d))
            last_spin = enc_raw

        sp_angle = (sp_angle + sp_speed) % 360
        scr_spin()

        if btn_event:
            btn_clear()
            diff = abs(sp_angle - sp_target)
            if diff > 180: diff = 360 - diff
            if diff <= 8:    pts = 100
            elif diff <= 20: pts = 60
            elif diff <= 40: pts = 30
            else:            pts = 0
            sp_score += pts
            scr_spin_result(diff, pts)
            time.sleep(2)
            sp_target = random.randint(0, 359)
            sp_speed  = 12
            sp_angle  = 0
            last_spin = enc_raw

        if not sw.value():
            t0 = time.ticks_ms()
            while not sw.value(): time.sleep_ms(10)
            if time.ticks_diff(time.ticks_ms(), t0) > 1000:
                btn_event = False
                sp_score  = 0
                last_menu = enc_raw
                state     = ST_MENU

    time.sleep_ms(10)

