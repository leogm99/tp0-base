package common

import (
	"math"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
	MaxPacketSize int
	BetBatchSize  int
}

// Client Entity that encapsulates how
type Client struct {
	config    ClientConfig
	conn      net.Conn
	betReader *BetReader
}

// NewClient Initializes a new client receiving the configuration
// and the bet as parameters
func NewClient(config ClientConfig, betReader *BetReader) *Client {
	client := &Client{
		config:    config,
		betReader: betReader,
	}
	return client
}

// splitPacketAtSize takes a buffer and splits it in chunks of at most
// `maxPacketSize` bytes each (configurable)
func splitPacketAtSize(buffer []byte, maxPacketSize int) [][]byte {
	splits := int(math.Ceil(float64(len(buffer)) / float64(maxPacketSize)))
	packets := make([][]byte, splits)
	for i := 0; i < splits; i += 1 {
		start := i * maxPacketSize
		end := int(math.Min(float64((i+1)*maxPacketSize), float64(len(buffer))))
		packets[i] = buffer[start:end]
	}
	return packets
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Fatalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// registers a channel to listen to the SIGTERM signal
// the channel is read-only
func (c *Client) registerShutdownSignal() <-chan os.Signal {
	signal_channel := make(chan os.Signal, 1)
	signal.Notify(signal_channel, syscall.SIGTERM)
	return signal_channel
}

func (c *Client) writeAll(buffer []byte) error {
	toSendBytes := len(buffer)
	currently_sent := 0

	for toSendBytes != currently_sent {
		sent, err := c.conn.Write(buffer[currently_sent:])
		// the socket was probably closed
		// when sent < len(buffer), `Write` returns a not nil error
		// that does not mean that the socket was closed, probably its because of buffer overflows at the sending side
		if (err != nil) && (sent == 0) {
			return err
		}
		currently_sent += sent
	}
	return nil
}

func (c *Client) readAll(bufferLength int) ([]byte, error) {
	currently_read := 0
	buffer := make([]byte, bufferLength)
	for currently_read != bufferLength {
		read, err := c.conn.Read(buffer[currently_read:])
		if (err != nil) && (read == 0) {
			return buffer, err
		}
		currently_read += read
	}
	return buffer, nil
}

// Run: Send best to the server and await its confirmation
func (c *Client) Run() {
	// Create the connection
	err := c.createClientSocket()
	if err != nil {
		log.Errorf("action: create_socket | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}

	// we defer the closing of the socket so as to not miss it
	defer c.conn.Close()
	for {
		bets, keep_reading, err := c.betReader.ReadChunk()
		if err != nil {
			log.Errorf(
				"action: read_chunk | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}
		if !keep_reading && len(bets) == 0 {
			return
		}
		// Serialize the bets in chunks
		betByteArrays := SerializeBets(bets, 1, keep_reading)

		// Write all bytes
		err = c.writeInPackets(betByteArrays)
		if err != nil {
			log.Errorf("action: write_packets | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}
		state, _ := DeserializeBetSavedState(c.readAll)
		if state == BetStateOk {
			log.Infof("action: bet_sent | result: success | client_id: %v",
				c.config.ID,
			)
		} else {
			log.Errorf("action: bet_sent | result: fail | client_id: %v",
				c.config.ID,
				err,
			)
			break
		}
		if !keep_reading {
			log.Infof("action: exit_client_loop | result: success | client_id: %v",
				c.config.ID,
			)
			break
		}
		time.Sleep(c.config.LoopPeriod)
	}
}

func (c *Client) writeInPackets(buffer []byte) error {
	// Split packet just in case it exceeds the maximum packet size
	packets := splitPacketAtSize(buffer, c.config.MaxPacketSize)
	// changed to index access to avoid copying the packets
	for idx := range packets {
		err := c.writeAll(packets[idx])
		if err != nil {
			return err
		}
	}
	return nil
}
