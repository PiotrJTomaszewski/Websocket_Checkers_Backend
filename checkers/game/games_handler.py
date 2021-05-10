import uuid
from .game_room import GameRoom
from .player import Player
from json import JSONEncoder


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GamesHandler(metaclass=Singleton):

    def __init__(self) -> None:
        self.rooms: list[GameRoom] = []
        self.players: list[Player] = {}

    def find_empty_room(self) -> GameRoom:
        for room in self.rooms:
            if not room.is_full():
                return room
        room = GameRoom()
        self.rooms.append(room)
        return room

    def get_player(self, uuid_str: str) -> Player:
        return self.players.get(uuid_str)

    def initialize_player(self, uuid_str: str = None) -> Player:
        player = Player(uuid_str)
        room = self.find_empty_room()
        in_room_id = room.add_player(player)
        player.set_game_room(room, in_room_id)
        self.players[player.get_uuid_str()] = player
        print(f'{len(self.players.keys())} players, {len(self.rooms)} rooms')
        return player

    def add_player(self, uuid_str: str = None) -> Player:
        if uuid_str is None:
            return self.initialize_player(None)
        player = self.players.get(uuid_str)
        if player is None:
            return self.initialize_player(uuid_str)
        else:
            return player
