from checkers.game.game_piece import GamePieceColor
from checkers.game import game_room

from uuid import UUID, uuid4
import time


class Player:
    def __init__(self, uuid_str: str = None) -> None:
        self.room: 'game_room.GameRoom' = None
        self.in_room_id: int = None
        self.uuid: UUID = None
        self.send_msg: function = None
        self.piece_color: GamePieceColor = None
        self.connection_lost_time = None
        if uuid_str is None:
            self.gen_uuid()
        else:
            self.set_uuid(uuid_str)

    def get_uuid_str(self) -> str:
        return str(self.uuid.hex)

    def gen_uuid(self) -> None:
        self.uuid = uuid4()

    def set_uuid(self, uuid_str: str) -> None:
        self.uuid = UUID(hex=uuid_str)

    def set_game_room(self, room: 'game_room.GameRoom', in_room_id: int) -> None:
        self.room = room
        self.in_room_id = in_room_id
        self.piece_color = GamePieceColor.LIGHT if self.in_room_id == self.room.light_player_id else GamePieceColor.DARK

    def set_send_msg_func(self, func: 'function') -> None:
        self.send_msg = func

    def mark_connected(self) -> None:
        self.connection_lost_time = None

    def mark_disconnected(self) -> None:
        self.connection_lost_time = time.time()

    def get_last_disconnection_time(self) -> float:
        return self.connection_lost_time
