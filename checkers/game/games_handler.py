from typing import List, Tuple
from checkers.messages import MessageType
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
        self.rooms: List[GameRoom] = []
        self.players: List[Player] = {}

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
                self.remove_room(room)
                print(f"Removing a room due to inactivity, {len(self.players.keys())} players and {len(self.rooms)} rooms left")

    def remove_room(self, room: GameRoom) -> None:
        for player in room.players:
            if player is not None:
                try:
                    del self.players[player.get_uuid_str()]
                except KeyError:
                    print(f"Couldn't find player with uuid {room.players[0]} while removing")
        self.rooms.remove(room)

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

    def add_player(self, uuid_str: str = None) -> Tuple[Player, bool]:
        # Returns True if new Player object was created
        if uuid_str is None:
            return self.initialize_player(None), True
        player = self.players.get(uuid_str)
        if player is None:
            return self.initialize_player(uuid_str), True
        else:
            return player, False

    def check_and_start_game(self, room: GameRoom) -> None:
        if room.can_game_start():
            room.start_game()
            room.players[0].send_msg(
                MessageType.START_GAME, {'piece_color': room.players[0].piece_color})
            room.players[1].send_msg(
                MessageType.START_GAME, {'piece_color': room.players[1].piece_color})
            print("Game started")

    def send_state(self, player: Player):
        if player.room.in_game:
            pieces = player.room.game.filter_pieces()
            player.send_msg(MessageType.CURRENT_STATE, {'piece_color': player.piece_color, 'game_state': player.room.game.game_state, 'pieces': pieces})

    def move_piece(self, player: Player, from_field: int, to_field: int) -> None:
        game: Game = player.room.game
        if game.get_piece_color(from_field) == player.piece_color:
            result: MoveResult = game.move_piece(from_field, to_field)
            if result.move_error != GameError.NO_ERROR:
                player.send_msg(MessageType.WRONG_MOVE, {'from_field': from_field, 'error': result.move_error})
            else:
                room: GameRoom = player.room
                room.players[0].send_msg(MessageType.MOVE_OK, {'from_field': from_field, 'to_field': to_field, 'end_turn': result.end_turn, 'promote': result.promote, 'captured_field': result.captured_piece_field})
                room.players[1].send_msg(MessageType.MOVE_OK, {'from_field': from_field, 'to_field': to_field, 'end_turn': result.end_turn, 'promote': result.promote, 'captured_field': result.captured_piece_field})
        else:
            player.send_msg(MessageType.WRONG_MOVE, {'from_field': from_field, 'error': GameError.NOT_YOUR_PIECE})
        self.check_victory(player)

    def check_victory(self, player: Player):
        game: Game = player.room.game
        if game.check_victory():
            room: GameRoom = player.room
            room.players[0].send_msg(MessageType.GAME_END, {'game_state': game.game_state})
            room.players[1].send_msg(MessageType.GAME_END, {'game_state': game.game_state})
            room.end_game()
