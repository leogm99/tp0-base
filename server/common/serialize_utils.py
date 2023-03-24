import struct


def serialize_u8(to_serialize: int) -> bytearray:
    return bytearray(struct.pack('B', to_serialize))


def serialize_u32(to_serialize: int) -> bytearray:
    return bytearray(struct.pack('!L', to_serialize))

def serialize_string_and_length(to_serialize: str) -> bytearray:
    str_serialized = to_serialize.encode()
    len_string_serialized = len(str_serialized)
    len_serialized = bytearray(struct.pack('!H', len_string_serialized))
    len_serialized.extend(str_serialized)
    return len_serialized