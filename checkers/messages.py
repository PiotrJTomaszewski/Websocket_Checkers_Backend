from enum import Enum
import struct

from .game.game import GamePiece


class MessageType(Enum):
    JOIN_NEW = 1
    JOIN_EXISTING = 2  # + uuid (32 bytes)
    MOVE = 3  # + from (1 byte) + to (1 byte)
    WELCOME = 4
    WELCOME_NEW = 5  # + uuid (32 bytes)
    START_GAME = 6  # + player color (1 byte)
    CURRENT_STATE = 7 # + color (1 byte) + game state (1 byte) + pieces (up to 24 * 3 bytes)
    WRONG_MOVE = 8  # + from (1 byte) + error code (1 byte)
    MOVE_OK = 9  # + from (1 byte) + to (1 byte) + end turn (1 byte) + promote (1 byte) + captured field number (1 byte)
    GAME_END = 10  # + game state (1 byte)


def encode_piece(piece: GamePiece) -> bytes:
    return struct.pack('!BBB', piece.color.value, piece.type.value, piece.field_no)


def encode_piece_list(pieces: list[GamePiece]) -> bytes:
    return b''.join([encode_piece(piece) for piece in pieces])
