import struct

# https://docs.python.org/3/library/struct.html#format-characters
def deserialize_u8(buffer):
    """
    Unpacks buffer into a uint8
    """
    return int(struct.unpack("!B", buffer)[0])

def deserialize_u16(buffer):
    """
    Unpacks buffer into a uint16 from network order (big endian into the machine endianness)
    """
    return int(struct.unpack("!H", buffer)[0])

def deserialize_string(buffer, string_length):
    """
    Unpacks buffer of `string_length` bytes into a utf8 string
    """
    return struct.unpack(f"{string_length}s", buffer)[0].decode()