from enum import Enum
import struct
from typing import List

from .game.game import GamePiece


class MessageType(Enum):
    JOIN_NEW = 1
    JOIN_EXISTING = 2  # + uuid (32 bytes)
    MOVE = 3  # + from (1 byte) + to (1 byte)
    WELCOME = 4
    WELCOME_NEW = 5  # + uuid (32 bytes)
    START_GAME = 6  # + player color (1 byte)
    CURRENT_STATE = 7 # + player color (1 byte) + game state (1 byte) + pieces (up to 24 bytes)
    WRONG_MOVE = 8  # + from (1 byte) + error code (1 byte)
    MOVE_OK = 9  # + from (1 byte) + to (1 byte) + end turn (1 byte) + promote (1 byte) + captured field number (1 byte)
    GAME_END = 10  # + game state (1 byte)


def encode_piece(piece: GamePiece) -> bytes:
    # bit 7 - type (0 - man, 1 - king)
    # bit 6 - color (0 - light, 1 - dark)
    packed = piece.field_no
    packed |= ((piece.color.value-1) << 6)
    packed |= ((piece.type.value-1) << 7)
    return struct.pack('!B', packed)


def encode_piece_list(pieces: List[GamePiece]) -> bytes:
    return b''.join([encode_piece(piece) for piece in pieces])
