from machine import UART
import time

finger = UART(2, baudrate=57600, tx=17, rx=16)

# =========================
# BASIC COMMANDS
# =========================
GET_IMAGE  = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x01\x00\x05'
IMAGE2TZ1  = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x04\x02\x01\x00\x08'
IMAGE2TZ2  = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x04\x02\x02\x00\x09'
REG_MODEL  = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x05\x00\x09'

# STORE (ID will be inserted dynamically)
def STORE_CMD(page_id):
    pid_high = (page_id >> 8) & 0xFF
    pid_low  = page_id & 0xFF
    packet = [0xEF,0x01,0xFF,0xFF,0xFF,0xFF,0x01,0x00,0x06,0x06,0x01,pid_high,pid_low]
    checksum = sum(packet[6:]) & 0xFFFF
    packet.append((checksum >> 8) & 0xFF)
    packet.append(checksum & 0xFF)
    return bytes(packet)

SEARCH = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x08\x04\x01\x00\x00\x00\xA3\x00\xB1'

# =========================
# SEND COMMAND
# =========================
def send_cmd(cmd, delay=1):
    finger.write(cmd)
    time.sleep(delay)
    if finger.any():
        return finger.read()
    return None

def get_status(res):
    if res and len(res) > 9:
        return res[9]
    return None

def extract_match(res):
    if res and len(res) >= 16:
        fid = res[10] << 8 | res[11]
        conf = res[12] << 8 | res[13]
        return fid, conf
    return None, None

# =========================
# ENROLL FUNCTION
# =========================
def enroll_finger(fid):
    print("\n--- ENROLL ID:", fid, "---")

    # Step 1
    print("Place finger...")
    while get_status(send_cmd(GET_IMAGE)) != 0x00:
        time.sleep(1)

    print("Image captured")
    send_cmd(IMAGE2TZ1)

    print("Remove finger...")
    time.sleep(2)

    # Step 2
    print("Place SAME finger again...")
    while get_status(send_cmd(GET_IMAGE)) != 0x00:
        time.sleep(1)

    print("Image captured again")
    send_cmd(IMAGE2TZ2)

    # Step 3: Create model
    if get_status(send_cmd(REG_MODEL)) != 0x00:
        print("❌ Failed to create model")
        return

    # Step 4: Store
    if get_status(send_cmd(STORE_CMD(fid))) == 0x00:
        print("✅ Stored with ID:", fid)
    else:
        print("❌ Store failed")

# =========================
# MATCH FUNCTION
# =========================
def match_finger():
    if get_status(send_cmd(GET_IMAGE)) != 0x00:
        return None

    if get_status(send_cmd(IMAGE2TZ1)) != 0x00:
        return None

    res = send_cmd(SEARCH)
    if get_status(res) == 0x00:
        return extract_match(res)

    return None

# =========================
# MAIN MENU
# =========================
while True:
    print("\n1: Enroll Finger")
    print("2: Match Finger")

    choice = input("Enter choice: ")

    if choice == '1':
        fid = int(input("Enter ID (1-127): "))
        enroll_finger(fid)

    elif choice == '2':
        print("Place finger to match...")
        result = match_finger()

        if result:
            fid, conf = result
            print("✅ MATCHED ID:", fid)
            print("Confidence:", conf)
        else:
            print("❌ No match")

    time.sleep(1)