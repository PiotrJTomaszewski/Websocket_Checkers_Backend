from checkers.game.game_board import GameBoard
from enum import Enum
from .game_board import GameBoard

class GameState(Enum):
    NOT_STARTED = 1
    LIGHT_TURN = 2
    DARK_TURN = 3
    LIGHT_WON = 4
    DARK_WON = 5
    TIE = 6

class GameError(Enum):
    NO_ERROR = 1
    CANT_MOVE_PIECE = 2
    ILLEGAL_MOVE = 3
    FIELD_TAKEN = 4
    NOT_KING = 5
    NOT_YOUR_TURN = 6

class Game:
    def __init__(self):
        self.game_state: GameState = GameState.NOT_STARTED
        self.game_error: GameError = GameError.NO_ERROR
        self.game_board: GameBoard = None

    def start_game(self):
        self.game_board = GameBoard()
        self.game_board.init_pieces()
