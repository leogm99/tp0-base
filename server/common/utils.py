import csv
import datetime
import time
import fcntl
from socket import socket

""" Bets storage location. """
STORAGE_FILEPATH = "./bets.csv"
""" Simulated winner number in the lottery contest. """
LOTTERY_WINNER_NUMBER = 7574


""" A lottery bet registry. """
class Bet:
    def __init__(self, agency: str, first_name: str, last_name: str, document: str, birthdate: str, number: str):
        """
        agency must be passed with integer format.
        birthdate must be passed with format: 'YYYY-MM-DD'.
        number must be passed with integer format.
        """
        self.agency = int(agency)
        self.first_name = first_name
        self.last_name = last_name
        self.document = document
        self.birthdate = datetime.date.fromisoformat(birthdate)
        self.number = int(number)

""" Checks whether a bet won the prize or not. """
def has_won(bet: Bet) -> bool:
    return bet.number == LOTTERY_WINNER_NUMBER

"""
Persist the information of each bet in the STORAGE_FILEPATH file.

It takes a shared lock to the underneath file, as it does not modify it,
so multiple processes can potentially read the file in parallel.
"""
def store_bets(bets: list[Bet]) -> None:
    with open(STORAGE_FILEPATH, 'a+') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for bet in bets:
            writer.writerow([bet.agency, bet.first_name, bet.last_name,
                             bet.document, bet.birthdate, bet.number])
        fcntl.flock(file, fcntl.LOCK_UN)

"""
Loads the information all the bets in the STORAGE_FILEPATH file.

It takes an exclusive look to the underneath file descriptor.
"""
def load_bets() -> list[Bet]:
    with open(STORAGE_FILEPATH, 'r') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            yield Bet(row[0], row[1], row[2], row[3], row[4], row[5])
        fcntl.flock(file, fcntl.LOCK_UN)


def recv_all(size: int, client_socket: socket):
    """
    Attemps to receive a full buffer of length `size`
    """
    current_received = 0
    output_buffer = bytearray()
    while size != current_received:
        try:
            curr_bytes = bytearray(client_socket.recv(size - current_received))
            current_received += len(curr_bytes)
            output_buffer.extend(curr_bytes)
        except OSError as _:
            break
    return output_buffer

def send_all(buffer: bytearray, client_socket: socket):
    """
    Attemps to send all the bytes in buffer 
    """
    current_sent = 0
    size = len(buffer)
    while current_sent != size:
        try:
            sent = client_socket.send(buffer[current_sent:size])
            current_sent += sent
        except OSError as _:
            break


def split_packet_at_size(buffer: bytearray, max_packet_size: int) -> list[bytearray]:
    """
    Splits a packet into chunks of at most `max_packet_size` bytes
    """
    from math import ceil
    splits = ceil(len(buffer) / max_packet_size)
    chunks = []
    for i in range(splits):
        chunks.append(buffer[i*max_packet_size:min((i+1)*max_packet_size, len(buffer))])
    return chunks