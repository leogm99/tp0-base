package common

import "encoding/binary"

/*
	Deserializes an unsigned byte
*/
func DeserializeU8(buffer []byte) uint8 {
	return uint8(buffer[0])
}

/*
	Deserializes buffer into an unsigned short in big endian ordering
*/
func DeserializeU16(buffer []byte) uint16 {
	return binary.BigEndian.Uint16(buffer)
}

/*
	Deserializes buffer into an unsigned int in big endian ordering
*/
func DeserializeU32(buffer []byte) uint32 {
	return binary.BigEndian.Uint32(buffer)
}

/*
	Deserializes byte buffer into a string (the buffer may encode a utf-8 string)
*/
func DeserializeString(buffer []byte) string {
	return string(buffer)
}
