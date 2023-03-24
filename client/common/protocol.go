package common

import (
	"bytes"
)

/*
	Serializes the bet object into an slice of bytes

	The variable length fields (strings) are prefixed with their length so that the receiver
	knows how much to read from the socket

	|name-length|        name       |surname-length|        surname       |document-length|        document       |birthdate-len|		birthdate   	|   bet   | lottery_id |
	|  2-bytes  | name-length bytes |    2 bytes   | surname-length bytes |    2 bytes    | document-length bytes |   2 bytes   | birthdate-length bytes| 2 bytes |   1 byte   |
*/

func serializeBet(b *Bet, lottery_id int) []byte {
	byteArrays := [][]byte{SerializeStringAndLengthToByteArray(b.PersonName),
		SerializeStringAndLengthToByteArray(b.PersonSurname),
		SerializeStringAndLengthToByteArray(b.PersonDocument),
		SerializeStringAndLengthToByteArray(b.PersonBirthDate),
		SerializeU16(b.PersonBet),
		SerializeU8(uint8(lottery_id)),
	}

	return bytes.Join(byteArrays, nil)
}

/*
	Serializes bets in chunks

	At the start of the message, we prepend 4 bytes representing the number of bets in the chunk.
	Also, a byte signaling if the server should keep listening is appended
*/
func SerializeBets(bs []Bet, lottery_id int, keep_reading bool) []byte {
	bsArrays := make([][]byte, len(bs)+2, len(bs)+2)
	bsArrays[0] = SerializeU32(uint32(len(bs)))
	for idx := range bs {
		bsArrays[1+idx] = serializeBet(&bs[idx], lottery_id)
	}
	if keep_reading {
		bsArrays[len(bsArrays)-1] = SerializeU8(uint8(1))
	} else {
		bsArrays[len(bsArrays)-1] = SerializeU8(uint8(0))
	}
	res := bytes.Join(bsArrays, nil)
	return res
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

/*
	Deserialize the list of documents of winners

	It firts reads 4 bytes which represent how many winners there are
	Then it simply reads 2 bytes representing the length of the document
	and reads that amount of bytes from the socket to receive the document
*/
func DeserializeWinners(readHandle func(int) ([]byte, error)) ([]string, error) {
	nWinnersBuffer, err := readHandle(4)
	if err != nil {
		return nil, err
	}
	nWinners := int(DeserializeU32(nWinnersBuffer))
	winnerDocuments := make([]string, 0, nWinners)
	for i := 0; i < nWinners; i += 1 {
		lengthDocumentBuffer, err := readHandle(2)
		if err != nil {
			return nil, err
		}
		lengthDocument := DeserializeU16(lengthDocumentBuffer)
		documentBuffer, err := readHandle(int(lengthDocument))
		if err != nil {
			return nil, err
		}
		winnerDocuments = append(winnerDocuments, DeserializeString(documentBuffer))
	}
	return winnerDocuments, nil
}
