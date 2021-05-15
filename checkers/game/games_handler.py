from .game_room import GameRoom
from .player import Player
from .game_piece import GamePieceColor
from .game import Game, GameError, GameState, MoveResult

from json import JSONEncoder
import time

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GamesHandler(metaclass=Singleton):
    INACTIVITY_TIMEOUT = 15 * 60

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

    def check_and_remove_inactive(self) -> None:
        for room in self.rooms:
            is_any_player_active: bool = False
            for player in room.players:
                if player is not None:
                    disc_time: float = player.get_last_disconnection_time()
                    if disc_time is None or (time.time() - disc_time < self.INACTIVITY_TIMEOUT):
                        is_any_player_active = True
            if not is_any_player_active:
                for player in room.players:
                    if player is not None:
                        try:
                            del self.players[player.get_uuid_str()]
                        except KeyError:
                            print(f"Couldn't find player with uuid {room.players[0]} while removing")
                self.rooms.remove(room)
                print(f"Removing a room due to inactivity, {len(self.players.keys())} players and {len(self.rooms)} rooms left")

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

    def get_pieces_list(self, game: Game):
        pieces = game.filter_pieces()
        pieces_dict_list = list(map(lambda piece: {'color': piece.get_color(
        ).value, 'type': piece.get_type().value, 'field_no': piece.get_field_no()}, pieces))
        return JSONEncoder().encode(pieces_dict_list)

    def check_and_start_game(self, room: GameRoom) -> None:
        if room.can_game_start():
            room.start_game()
            pieces_enc = self.get_pieces_list(room.game)
            room.players[0].send_msg(
                'StartGame', [str(room.players[0].piece_color.value), pieces_enc])
            room.players[1].send_msg(
                'StartGame', [str(room.players[1].piece_color.value), pieces_enc])
            print("Game started")

    def send_state(self, player: Player):
        # TODO: Finish
        if player.room.in_game:
            pieces = self.get_pieces_list(player.room.game)
            player.send_msg('CurrentState', [str(player.piece_color.value), str(
                player.room.game.game_state.value), pieces])

    def move_piece(self, player: Player, from_field: int, to_field: int) -> None:
        game: Game = player.room.game
        if game.get_piece_color(from_field) == player.piece_color:
            result: MoveResult = game.move_piece(from_field, to_field)
            if result.move_error != GameError.NO_ERROR:
                player.send_msg('WrongMove', [str(from_field), str(result.move_error.value)])
            else:
                room: GameRoom = player.room
                room.players[0].send_msg('Move', [str(from_field), str(to_field), str(result.end_turn), str(result.promote), str(result.captured_piece_field)])
                room.players[1].send_msg('Move', [str(from_field), str(to_field), str(result.end_turn), str(result.promote), str(result.captured_piece_field)])
        else:
            player.send_msg('WrongMove', [str(from_field), str(GameError.NOT_YOUR_PIECE.value)])
        self.check_victory(player)

    def check_victory(self, player: Player):
        game: Game = player.room.game
        if game.check_victory():
            room: GameRoom = player.room
            room.players[0].send_msg('GameEnd', [str(game.game_state.value)])
            room.players[1].send_msg('GameEnd', [str(game.game_state.value)])
