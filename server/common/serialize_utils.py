import struct


def serialize_u8(to_serialize: int) -> bytearray:
    return bytearray(struct.pack('B', to_serialize))