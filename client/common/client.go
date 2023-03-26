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
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	bet    *Bet
}

// NewClient Initializes a new client receiving the configuration
// and the bet as parameters
func NewClient(config ClientConfig, bet *Bet) *Client {
	client := &Client{
		config: config,
		bet:    bet,
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
		sent, err := c.conn.Write(buffer[currently_sent:toSendBytes])
		currently_sent += sent
		// the socket was probably closed
		// when sent < len(buffer), `Write` returns a not nil error
		// that does not mean that the socket was closed, probably its because of buffer overflows at the sending side
		if (err != nil) && (sent == 0) {
			return err
		}
	}
	return nil
}

func (c *Client) readAll(bufferLength int) ([]byte, error) {
	currently_read := 0
	buffer := make([]byte, bufferLength)
	for currently_read != bufferLength {
		read, err := c.conn.Read(buffer[currently_read:bufferLength])
		currently_read += read
		if (err != nil) && (read == 0) {
			return buffer, err
		}
	}
	return buffer, nil
}

// StartClient: Send the bet to the server and await its confirmation
func (c *Client) StartClient() {
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

	// Serialize the bet
	betByteArray := SerializeBet(c.bet)

	// Split packet just in case it exceeds the maximum size
	packets := splitPacketAtSize(betByteArray, c.config.MaxPacketSize)
	for _, p := range packets {
		// Write all bytes
		err = c.writeAll(p)
		if err != nil {
			log.Errorf("action: write_all | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}
	}
	betState, err := DeserializeBetSavedState(c.readAll)
	if err == nil && betState == BetStateOk {
		log.Infof("action: bet_sent | result: success | dni: %v | number: %v",
			c.bet.PersonDocument,
			c.bet.PersonBet,
		)
	} else if err != nil || betState == BetStateErr {
		log.Error("action: bet_sent | result: failed | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
}
