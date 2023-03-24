import socket
import logging
import signal
from common.protocol import deserialize_bets, serialize_saved_bets_status, serialize_bet_winners, SavedBetState
from common.utils import store_bets, load_bets, has_won
N_AGENCIES = 5

class Server:
    def __init__(self, port, listen_backlog, max_packet_size):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._closed = False
        self._max_packet_size = max_packet_size

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        logging.info('Registering SIGTERM signal')
        signal.signal(signal.SIGTERM, lambda _n,_f: self.stop())
        handled_agencies = 0
        client_agency_sockets = []
        try:
            while not self._closed and handled_agencies != N_AGENCIES:
                # accept throws an exception if the socket is closed
                client_sock = self.__accept_new_connection()
                agency_id = self.__receive_agency_bets(client_sock)
                if agency_id == -1:
                    raise ValueError("Invalid agency id")
                client_agency_sockets.append((agency_id, client_sock))
                handled_agencies += 1
                logging.info(f'{handled_agencies}')
        except OSError as e:
            if self._closed:
                logging.info('action: shutdown_acceptor | result: success')
            else:
                logging.info(f'action: handle_client_connection | result: failed | error: {e}')
                self.stop()
        except BaseException as e:
            logging.info(f'action: receive_agency_bets | result: failed | error: {e}')
            self.stop()
        if self._closed:
            return
        logging.info('action: raffle | result: success')
        try:
            for agency_id, sock in client_agency_sockets:
                self.__send_winners(agency_id, sock)
        except OSError as e:
            logging.info(f'action: send_winners | result: failed | error: {e}')
        self.stop()

    
    def __recv_all(self, size: int, client_socket: socket.socket):
        current_received = 0
        output_buffer = bytearray()
        while size != current_received:
            try:
                curr_bytes = bytearray(client_socket.recv(size - current_received))
                current_received += len(curr_bytes)
                output_buffer.extend(curr_bytes)
            except OSError as e:
                logging.error(f'action: recv_all | result: failed | reason: {e}')
                break
        return output_buffer

    def __send_all(self, buffer: bytearray, client_socket: socket.socket):
        current_sent = 0
        size = len(buffer)
        while current_sent != size:
            try:
                sent = client_socket.send(buffer[current_sent:size])
                current_sent += sent
            except OSError as e:
                logging.error(f'action: send_all | result: failed | reason: {e}')
                break

    def __receive_agency_bets(self, client_sock) -> int:
        """
        Read message from a specific client socket and closes the socket
        Returns the agency_id associated with the client

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        recv_handle = lambda len_buffer: self.__recv_all(len_buffer, client_sock)
        agency = -1
        while True:
            try:
                bets, keep_reading = deserialize_bets(recv_handle) 
                logging.info('action: storing-bets | result: in progress')
                store_bets(bets)
                self.__send_all(serialize_saved_bets_status(SavedBetState.OK), client_sock)
                logging.info('action: storing-bets | result: success')
                if not keep_reading:
                    agency = bets[0].agency
                    logging.info('action: stop_reading | result:success')
                    break
            except OSError as e:
                self.__send_all(serialize_saved_bets_status(SavedBetState.ERR))
                break
            except BaseException as e:
                logging.error(f'action: bet_stored | result: failed | error: {e}')
                break
        return agency


    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c


    def stop(self):
        """
        Stops the server by shutting and closing down the current socket
        """
        if self._closed:
            logging.error("action: stop | result: failed | error: Server was already closed")
            raise ValueError("Server already closed")

        logging.info('action: stop_server | result: in_progress')
        # shutdown both channels
        self._server_socket.shutdown(socket.SHUT_RDWR)
        # we only need to close this socket as the client_socket will be closed by `__handle_client_connection`
        # even if the execution continues here because of a signal
        # close
        self._server_socket.close()
        self._closed = True
        logging.info('action: stop_server | result: success')

    def __send_winners(self, agency_id: int, client_socket: socket.socket):
        winners = list(filter(lambda bet: (bet.agency == agency_id) and has_won(bet), load_bets()))
        winners_serialized = serialize_bet_winners(winners)
        packets = _split_packet_at_size(winners_serialized, self._max_packet_size)
        for p in packets:
            self.__send_all(p, client_socket)



def _split_packet_at_size(buffer: bytearray, max_packet_size: int) -> list[bytearray]:
    """
    Splits a packet into chunks of at most `max_packet_size` bytes
    """
    from math import ceil
    splits = ceil(len(buffer) / max_packet_size)
    chunks = []
    for i in range(splits):
        chunks.append(buffer[i*max_packet_size:min((i+1)*max_packet_size, len(buffer))])
    return chunks
