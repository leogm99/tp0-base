package common

import (
	"encoding/csv"
	"io"
	"os"
	"strconv"

	log "github.com/sirupsen/logrus"
)

type BetReader struct {
	config    ClientConfig
	file      *os.File
	reader    *csv.Reader
	cacheLine []string
}

func NewBetReader(filePath string, config ClientConfig) (*BetReader, error) {
	file, err := os.Open(filePath)
	if err != nil {
		log.Fatalf(
			"action: open_bet_csv | result: fail | client_id: %v | error: %v",
			config.ID,
			err,
		)
		return nil, err
	}

	return &BetReader{
		config:    config,
		file:      file,
		reader:    csv.NewReader(file),
		cacheLine: nil,
	}, nil
}

// Reads csv in chunks. The size of the batch is configurable
// It returns an array of bets,
// a flag to indicate if there is anything left to read
// and an error

func (b *BetReader) ReadChunk() ([]Bet, bool, error) {
	batch := b.config.BetBatchSize
	bets := make([]Bet, 0)
	if b.cacheLine != nil {
		new_bet, err := b.buildBet(b.cacheLine)
		if err != nil {
			log.Info("action: build_bet | result: failed | client_id: %v | error: %v",
				b.config.ID,
				err,
			)
			return nil, false, err
		}
		b.cacheLine = nil
		bets = append(bets, new_bet)
		batch -= 1
	}
	for i := 0; i < batch; i += 1 {
		lines, err := b.reader.Read()
		if err == io.EOF {
			return bets, false, nil
		} else if err != nil {
			return nil, false, err
		}
		bet, err := b.buildBet(lines)
		bets = append(bets, bet)
		if err != nil {
			return nil, false, err
		}
	}
	return bets, b.checkIfRemainsLine(), nil
}

func (b *BetReader) buildBet(lines []string) (Bet, error) {
	// we could use reflection here but maybe this is easier
	bet, err := strconv.ParseUint(lines[4], 10, 32)
	if err != nil {
		return Bet{}, err
	}
	return Bet{
		PersonName:      lines[0],
		PersonSurname:   lines[1],
		PersonDocument:  lines[2],
		PersonBirthDate: lines[3],
		PersonBet:       uint16(bet),
	}, nil
}

func (b *BetReader) setCacheLine(line []string) {
	b.cacheLine = line
}

// Tries to read the next line
// If it fails with EOF,
// it means we have exhausted all the bets in the file
// So no more bets are available to read
// Otherwise, if a line is read, it is "cached" in the BetReader
// for future access.
func (b *BetReader) checkIfRemainsLine() bool {
	shouldKeepReading := true
	// attempt to read a line
	line, err := b.reader.Read()
	if err == io.EOF {
		shouldKeepReading = false
	} else {
		// cache the line
		b.setCacheLine(line)
	}
	return shouldKeepReading
}
