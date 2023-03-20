import socket
import logging
import signal


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._closed = False

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

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            msg = client_sock.recv(1024).rstrip().decode('utf-8')
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            # TODO: Modify the send to avoid short-writes
            client_sock.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
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

        logging.info('action: stop_server | result: in_progress')
        # shutdown both channels
        self._server_socket.shutdown(socket.SHUT_RDWR)
        # we only need to close this socket as the client_socket will be closed by `__handle_client_connection`
        # even if the execution continues here because of a signal
        # close
        self._server_socket.close()
        self._closed = True
        logging.info('action: stop_server | result: success')
