import socket
import logging
import signal
from common.server_pool import ServerPool
from common.client_handler import ClientHandler
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

        pool = ServerPool()
        logging.info('action: server_pool_start | result: in progress')
        pool.start()
        logging.info('action: server_pool_start | result: success')

        handled_agencies = 0
        try:
            while not self._closed and handled_agencies != N_AGENCIES:
                # accept throws an exception if the socket is closed
                client_sock = self.__accept_new_connection()
                handler = ClientHandler(client_socket=client_sock, max_packet_size=self._max_packet_size)
                pool.apply(handler)
                handled_agencies += 1
        except OSError as e:
            if self._closed:
                logging.info('action: shutdown_acceptor | result: success')
            else:
                logging.info(f'action: handle_client_connection | result: failed | error: {e}')
        except BaseException as e:
            logging.info(f'action: apply_client_handler | result: failed | error: {e}')
        finally:
            pool.stop()
            self.stop()
        from time import sleep
        sleep(1000)
    
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
