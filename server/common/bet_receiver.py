from typing import Any
from socket import socket
from multiprocessing import get_logger, Queue
from common.utils import send_all, recv_all, store_bets, load_bets, has_won, split_packet_at_size
from common.protocol import deserialize_bets, serialize_saved_bets_status, SavedBetState, serialize_bet_winners
from common.raffle_winners_sender import RaffleWinnersSender

class BetReceiver:
    def __init__(self, client_socket: socket, max_packet_size: int) -> None:
        self._client_socket = client_socket
        self._max_packet_size = max_packet_size

    def __run(self):
        agency_id = self.__receive_agency_bets()
        return RaffleWinnersSender(agency_id=agency_id, 
                            client_socket=self._client_socket, 
                            max_packet_size=self._max_packet_size)



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

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.__run()