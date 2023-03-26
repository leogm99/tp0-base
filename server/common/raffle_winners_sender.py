from socket import socket, SHUT_RDWR
from typing import Any
from common.utils import send_all, load_bets, has_won, split_packet_at_size
from common.protocol import serialize_bet_winners

class RaffleWinnersSender:
    def __init__(self, agency_id: int, max_packet_size: int, client_socket: socket) -> None:
        self._agency_id = agency_id
        self._client_socket = client_socket
        self._max_packet_size = max_packet_size

    def __run(self):
        return self.__send_winners()

    def __send_winners(self):
        winners = list(filter(lambda bet: (bet.agency == self._agency_id) and has_won(bet), load_bets()))
        winners_serialized = serialize_bet_winners(winners)
        packets = split_packet_at_size(winners_serialized, self._max_packet_size)
        for p in packets:
            send_all(p, self._client_socket)
        # shutdown and close the client socket
        self._client_socket.shutdown(SHUT_RDWR)
        self._client_socket.close()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.__run()