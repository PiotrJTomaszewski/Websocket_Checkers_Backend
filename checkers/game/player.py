from . import game_room

from uuid import UUID, uuid4


class Player:
    def __init__(self, uuid_str: str = None) -> None:
        self.is_in_game = False
        self.room = None
        self.in_room_id = None
        self.uuid = None
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
