import machine
import time

# Setup ADC pin (GPIO34 is input-only, best for analog)
mq2 = machine.ADC(machine.Pin(34))

# Configure ADC
mq2.atten(machine.ADC.ATTN_11DB)   # Full range: 0 - 3.3V
mq2.width(machine.ADC.WIDTH_12BIT) # 0 - 4095

while True:
    gas_value = mq2.read()  # Read analog value
    
    print("Gas Sensor Value:", gas_value)
    
    # Simple threshold detection
    if gas_value > 2000:
        print("⚠️ Gas Leakage Detected!")
    else:
        print("✅ Air is Safe")
    
    print("----------------------")
    time.sleep(1)