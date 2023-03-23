from common.deserialize_utils import deserialize_bool, deserialize_u8, deserialize_u16, deserialize_u32, deserialize_string
from common.serialize_utils import serialize_u8
from common.utils import Bet
from enum import Enum
from typing import Union

def deserialize_bet(recv):
    """
    Deserializes the bet into its fields from the payload received by the client

    recv is a handle to a function wrapping `recv`
    """
    person_name_size = deserialize_u16(recv(2))
    person_name = deserialize_string(recv(person_name_size), person_name_size)

    person_surname_size = deserialize_u16(recv(2))
    person_surname = deserialize_string(recv(person_surname_size), person_surname_size)

    person_document_size = deserialize_u16(recv(2))
    person_document = deserialize_string(recv(person_document_size), person_document_size)

    person_birthdate_size = deserialize_u16(recv(2))
    person_birthdate = deserialize_string(recv(person_birthdate_size), person_birthdate_size)

    person_bet = deserialize_u16(recv(2))

    lottery_id = deserialize_u8(recv(1))
    return Bet(lottery_id, 
               person_name, 
               person_surname, 
               person_document, 
               person_birthdate, 
               person_bet)


def deserialize_bets(recv) -> Union[list[Bet], bool]:
    bets_in_chunk = deserialize_u32(recv(4))
    bets = []
    for _ in range(bets_in_chunk):
        bet = deserialize_bet(recv)
        bets.append(bet)
    keep_reading = deserialize_bool(recv(1))
    return bets, keep_reading


class SavedBetState(Enum):
    OK = 0
    ERR = 1


# The state of saving the bet is represented with a byte (0 -> Ok, 1 -> Some kind of error)
def serialize_saved_bets_status(state: SavedBetState) -> bytearray:
    """
    Serializes the state of the bet after the attempt at persisting it
    """

    return serialize_u8(state.value)
