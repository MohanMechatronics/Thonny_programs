# ws_msgpack.py
# MicroPython library to pack Python dicts to MsgPack
# and send them as binary WebSocket frames.

import struct

# ---------------------------
# Minimal MsgPack Packer
# ---------------------------

def packb(obj):
    """Pack a Python object into MsgPack binary."""
    buf = bytearray()
    _pack(obj, buf)
    return bytes(buf)


def _pack(obj, buf):
    if obj is None:
        buf.append(0xc0)

    elif isinstance(obj, bool):
        buf.append(0xc3 if obj else 0xc2)

    elif isinstance(obj, int):
        if 0 <= obj <= 0x7f:
            buf.append(obj)
        elif -32 <= obj < 0:
            buf.append(0xe0 | (obj + 32))
        elif -128 <= obj <= 127:
            buf.extend([0xd0, obj & 0xff])
        elif -32768 <= obj <= 32767:
            buf.extend([0xd1, (obj >> 8) & 0xff, obj & 0xff])
        else:
            buf.extend([
                0xd2,
                (obj >> 24) & 0xff,
                (obj >> 16) & 0xff,
                (obj >> 8) & 0xff,
                obj & 0xff
            ])

    elif isinstance(obj, float):
        buf.append(0xca)
        buf.extend(struct.pack('>f', obj))

    elif isinstance(obj, str):
        b = obj.encode()
        l = len(b)
        if l < 32:
            buf.append(0xa0 | l)
        else:
            buf.extend([0xd9, l])
        buf.extend(b)

    elif isinstance(obj, bytes) or isinstance(obj, bytearray):
        l = len(obj)
        buf.extend([0xc4, l])
        buf.extend(obj)

    elif isinstance(obj, list):
        l = len(obj)
        if l < 16:
            buf.append(0x90 | l)
        else:
            buf.extend([0xdc, (l >> 8) & 0xff, l & 0xff])
        for item in obj:
            _pack(item, buf)

    elif isinstance(obj, dict):
        l = len(obj)
        if l < 16:
            buf.append(0x80 | l)
        else:
            buf.extend([0xde, (l >> 8) & 0xff, l & 0xff])
        for k, v in obj.items():
            _pack(k, buf)
            _pack(v, buf)

    else:
        raise TypeError("Unsupported type for MsgPack: {}".format(type(obj)))


# ---------------------------
# WebSocket Binary Sender
# (works with uwebsockets.py)
# ---------------------------

def send_msgpack(ws, obj):
    """
    Encode a dict as MsgPack and send over WebSocket as binary frame.
    ws = uwebsockets.connect("ws://ip:port/")
    """
    # Patch ws.send to use opcode 0x82 (binary)
    # Most uwebsockets clients default to 0x81 (text)
    bin_data = packb(obj)
    ws.send(bin_data)   # must be patched for binary opcode
