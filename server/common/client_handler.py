from typing import Any
from socket import socket, SHUT_RDWR
from multiprocessing import get_logger
from common.utils import send_all, recv_all, store_bets, load_bets, has_won, split_packet_at_size
from common.protocol import deserialize_bets, serialize_saved_bets_status, SavedBetState, serialize_bet_winners

class ClientHandler:
    def __init__(self, client_socket: socket, max_packet_size: int) -> None:
        self._client_socket = client_socket
        self._max_packet_size = max_packet_size

    def __run(self):
        agencyId = self.__receive_agency_bets()
        if agencyId != -1:
            self.__send_winners(agencyId)

        self._client_socket.shutdown(SHUT_RDWR)
        self._client_socket.close()


    def __receive_agency_bets(self) -> int:
        logger = get_logger()
        """
        Read message from a specific client socket and closes the socket
        Returns the agency_id associated with the client

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        recv_handle = lambda len_buffer: recv_all(len_buffer, self._client_socket)
        agency = -1
        while True:
            try:
                bets, keep_reading = deserialize_bets(recv_handle) 
                logger.info('action: storing-bets | result: in progress')
                store_bets(bets)
                send_all(serialize_saved_bets_status(SavedBetState.OK), self._client_socket)
                logger.info('action: storing-bets | result: success')
                if not keep_reading:
                    agency = bets[0].agency
                    logger.info('action: stop_reading | result:success')
                    break
            except OSError as e:
                send_all(serialize_saved_bets_status(SavedBetState.ERR))
                break
            except BaseException as e:
                logger.error(f'action: bet_stored | result: failed | error: {e}')
                break
        return agency

    def __send_winners(self, agency_id: int):
        winners = list(filter(lambda bet: (bet.agency == agency_id) and has_won(bet), load_bets()))
        winners_serialized = serialize_bet_winners(winners)
        packets = split_packet_at_size(winners_serialized, self._max_packet_size)
        for p in packets:
            send_all(p, self._client_socket)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.__run()