import uuid
from .game_room import GameRoom
from .player import Player
from .game_board import GameBoard
from .game_piece import GamePieceColor

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

    def add_player(self, uuid_str: str = None) -> tuple[Player, bool]:
        # Returns True if new Player object was created
        if uuid_str is None:
            return self.initialize_player(None), True
        player = self.players.get(uuid_str)
        if player is None:
            return self.initialize_player(uuid_str), True
        else:
            return player, False

    def get_pieces_list(self, game_board: GameBoard):
        pieces = game_board.flatten_pieces()
        pieces_dict_list = list(map(lambda piece: {'color': piece.get_color().value, 'type': piece.get_type().value, 'field_no': piece.get_field_no()}, pieces))
        return JSONEncoder().encode(pieces_dict_list)

    def check_and_start_game(self, room: GameRoom) -> None:
        if room.can_game_start():
            room.start_game()
            pieces_enc = self.get_pieces_list(room.game.game_board)
            room.players[0].send_msg('StartGame', [str(GamePieceColor.LIGHT.value), pieces_enc])
            room.players[1].send_msg('StartGame', [str(GamePieceColor.DARK.value), pieces_enc])
            print("Game started")

    def send_state(self, player: Player):
        # TODO: Finish
        if player.room.in_game:
            pieces = self.get_pieces_list(player.room.game.game_board)
            color_val = player.in_room_id + 1
            player.send_msg('CurrentState', [str(color_val), str(player.room.game.game_state.value), pieces])
