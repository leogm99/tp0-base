import socket
import logging
import signal
from common.protocol import deserialize_bet, serialize_saved_bets_status, SavedBetState
from common.utils import store_bets


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
        while not self._closed:
            # accept throws an exception if the socket is closed
            try:
                client_sock = self.__accept_new_connection()
            except OSError as e:
                if self._closed:
                    logging.info('action: accept_new_connection | result: failed (expected) | reason: acceptor socket was already closed')
                else:
                    logging.info(f'action: accept_new_connection | result: failed | error: {e}')
                break
            self.__handle_client_connection(client_sock)

    
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

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        recv_handle = lambda len_buffer: self.__recv_all(len_buffer, client_sock)

        def __send_bet_state(state):
            saved_status = serialize_saved_bets_status(state)
            packets = _split_packet_at_size(saved_status, self._max_packet_size)
            for p in packets:
                self.__send_all(p, client_sock)
            
        try:
            bet = deserialize_bet(recv_handle) 
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]}')
            try:
                store_bets([bet])
                __send_bet_state(SavedBetState.OK)
                logging.info(f'action: bet_stored | result: success | dni: {bet.document} | number: {bet.number}')
            except BaseException as e:
                logging.error(f'action: bet_stored | result: failed | error: {e}')
                __send_bet_state(SavedBetState.ERR)

        except OSError as e:
            logging.error(f'action: receive_message | result: fail | error: {e}')
        finally:
            client_sock.close()

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