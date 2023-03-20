package common

import "bytes"

/*
	Serializes the bet object into an slice of bytes

	The variable length fields (strings) are prefixed with their length so that the receiver
	knows how much to read from the socket

	|name-length|        name       |surname-length|        surname       |document-length|        document       |birthdate-len|		birthdate   	|   bet   | lottery_id |
	|  2-bytes  | name-length bytes |    2 bytes   | surname-length bytes |    2 bytes    | document-length bytes |   2 bytes   | birthdate-length bytes| 2 bytes |   1 byte   |
*/

func SerializeBet(b *Bet) []byte {
	byteArrays := [][]byte{SerializeStringAndLengthToByteArray(b.PersonName),
		SerializeStringAndLengthToByteArray(b.PersonSurname),
		SerializeStringAndLengthToByteArray(b.PersonDocument),
		SerializeStringAndLengthToByteArray(b.PersonBirthDate),
		SerializeU16(b.PersonBet),
		SerializeU8(b.LotteryId),
	}

	return bytes.Join(byteArrays, nil)
}

const (
	BetStateOk = iota
	BetStateErr
)

/*
	Deserialize the bet state after the attempt of persisting it

	It reads one byte from the `readHandle` and returns the corresponding state.
*/
func DeserializeBetSavedState(readHandle func(int) ([]byte, error)) (uint8, error) {
	buffer, err := readHandle(1)
	if err != nil {
		return BetStateErr, err
	}
	if DeserializeU8(buffer) == BetStateOk {
		return BetStateOk, nil
	}
	return BetStateErr, nil
}
