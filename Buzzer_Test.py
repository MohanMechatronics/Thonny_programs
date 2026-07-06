from machine import Pin, PWM
import time

# --- Configuration ---
BUZZER_PIN = 4

# Emergency alert tone frequencies (Hz)
HIGH_TONE = 2000   # High pitch
LOW_TONE  = 1000   # Low pitch

# Timing (milliseconds)
BEEP_ON    = 150   # Duration tone is ON
BEEP_OFF   = 80    # Short gap between beeps
BURST_GAP  = 400   # Gap between bursts
CYCLE_GAP  = 800   # Gap between full alert cycles

# Number of beeps per burst
BEEPS_PER_BURST = 3

# --- Setup ---
buzzer = PWM(Pin(BUZZER_PIN), freq=HIGH_TONE, duty=0)

def tone_on(freq, duty=512):
    """Play a tone at given frequency. Duty 0-1023."""
    buzzer.freq(freq)
    buzzer.duty(duty)

def tone_off():
    """Silence the buzzer."""
    buzzer.duty(0)

def beep(freq, duration_ms, duty=512):
    """Single beep at a frequency for a duration."""
    tone_on(freq, duty)
    time.sleep_ms(duration_ms)
    tone_off()

def emergency_burst():
    """
    One burst = 3 rapid alternating high/low beeps
    Mimics a real emergency siren pattern.
    """
    for i in range(BEEPS_PER_BURST):
        # High tone
        beep(HIGH_TONE, BEEP_ON)
        time.sleep_ms(BEEP_OFF)
        # Low tone
        beep(LOW_TONE, BEEP_ON)
        time.sleep_ms(BEEP_OFF)

def wail_effect(duration_ms=600, steps=30):
    """
    Smooth rising and falling wail (siren sweep effect).
    Sweeps from LOW_TONE to HIGH_TONE and back.
    """
    step_time = duration_ms // (steps * 2)

    # Rising
    for i in range(steps):
        freq = LOW_TONE + int((HIGH_TONE - LOW_TONE) * i / steps)
        tone_on(freq)
        time.sleep_ms(step_time)

    # Falling
    for i in range(steps, 0, -1):
        freq = LOW_TONE + int((HIGH_TONE - LOW_TONE) * i / steps)
        tone_on(freq)
        time.sleep_ms(step_time)

    tone_off()

# --- Main Alert Loop ---
print("Emergency Alert Active on GPIO", BUZZER_PIN)
print("Press CTRL+C to stop.")

try:
    while True:
        # Phase 1: Rapid burst beeps
        emergency_burst()
        time.sleep_ms(BURST_GAP)

        # Phase 2: Wail / siren sweep
        wail_effect(duration_ms=700, steps=40)
        time.sleep_ms(BURST_GAP)

        # Phase 3: Another rapid burst
        emergency_burst()
        time.sleep_ms(CYCLE_GAP)   # Pause before repeating full cycle

except KeyboardInterrupt:
    tone_off()
    buzzer.deinit()
    print("Buzzer stopped.")