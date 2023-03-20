package common

import "encoding/binary"

func SerializeU8(toSerialize uint8) []byte {
	payload_buffer := make([]byte, 1)
	payload_buffer[0] = toSerialize
	return payload_buffer
}

// Returns the 2-byte value serialized in big endian
func SerializeU16(toSerialize uint16) []byte {
	payload_buffer := make([]byte, 2)
	binary.BigEndian.PutUint16(payload_buffer, toSerialize)
	return payload_buffer
}

// Returns the string as a byte slice
func SerializeString(toSerialize string) []byte {
	return []byte(toSerialize)
}

func SerializeStringAndLengthToByteArray(value string) []byte {
	valueByteArray := SerializeString(value)
	return append(SerializeU16(uint16(len(valueByteArray))), valueByteArray...)
}
