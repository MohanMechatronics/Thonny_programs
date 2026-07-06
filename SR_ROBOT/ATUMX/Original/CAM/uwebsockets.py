# MicroPython WebSocket client that supports:
# - sending binary frames
# - receiving binary frames
# - receiving text frames
# Works on ESP32 / ESP8266 / ESP32-CAM

import usocket as socket
import ubinascii
import urandom
import struct

class WebSocket:
    def __init__(self, sock):
        self.sock = sock

    # -------------------------
    # SEND (binary by default)
    # -------------------------
    def send(self, data, binary=True):
        if isinstance(data, str):
            data = data.encode()

        # opcode: 0x2 = binary frame, 0x1 = text frame
        opcode = 0x82 if binary else 0x81

        header = bytearray(2)
        header[0] = opcode
        length = len(data)

        if length < 126:
            header[1] = length
            self.sock.send(header + data)

        else:
            header[1] = 126
            ext = struct.pack("!H", length)
            self.sock.send(header + ext + data)

    # -------------------------
    # RECEIVE (supports binary)
    # -------------------------
    def recv(self):
        try:
            # --- Read header ---
            hdr = self.sock.recv(2)
            if not hdr:
                return None

            opcode = hdr[0] & 0x0F
            masked = hdr[1] & 0x80
            length = hdr[1] & 0x7F

            # Extended lengths
            if length == 126:
                ext = self.sock.recv(2)
                length = struct.unpack("!H", ext)[0]
            elif length == 127:
                # Not expected but safe
                ext = self.sock.recv(8)
                length = struct.unpack("!Q", ext)[0]

            # Masking key (server usually sends unmasked)
            mask = self.sock.recv(4) if masked else None

            # ---- READ FULL PAYLOAD ----
            data = bytearray()
            while len(data) < length:
                chunk = self.sock.recv(length - len(data))
                if not chunk:
                    break
                data.extend(chunk)

            # DEBUG PRINT
            print("opcode:", opcode, "len:", length, "data:", data)

            # Unmask if needed
            if mask:
                for i in range(length):
                    data[i] ^= mask[i % 4]

            # BINARY FRAME
            if opcode == 0x2:
                return bytes(data)

            # TEXT FRAME
            if opcode == 0x1:
                return data.decode()

            # PING FRAME
            if opcode == 0x9:
                # Send pong
                self.send(b"", binary=True)
                return None

            # CLOSE or unsupported
            return None

        except Exception as e:
            print("recv error:", e)
            return None


# -------------------------
# CONNECT to a WS server
# -------------------------
def connect(uri):
    assert uri.startswith("ws://")

    host_port, path = uri[5:].split("/", 1)
    path = "/" + path

    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 80

    addr = socket.getaddrinfo(host, port)[0][-1]
    sock = socket.socket()
    sock.connect(addr)

    key = ubinascii.b2a_base64(urandom.getrandbits(16).to_bytes(2, "big"))[:-1]

    handshake = (
        "GET {} HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Key: {}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    ).format(path, host, key.decode()).encode()

    sock.send(handshake)
    response = sock.recv(1024)

    if b"101" not in response:
        raise OSError("WebSocket handshake failed")

    return WebSocket(sock)
