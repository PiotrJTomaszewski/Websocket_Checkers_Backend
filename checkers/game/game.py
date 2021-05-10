from checkers.game.game_room import GameRoom
from checkers.game.game_piece import GamePiece, GamePieceColor, GamePieceType
from enum import Enum


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


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class MoveResult:
    def __init__(self, move_error: GameError, end_turn: bool = None, captured_piece_field: int = None) -> None:
        self.move_error = move_error
        self.end_turn = end_turn
        self.captured_piece_field = captured_piece_field


class Game:
    board_width = 4
    board_height = 8

    def __init__(self):
        self.game_state: GameState = GameState.NOT_STARTED
        self.game_error: GameError = GameError.NO_ERROR
        self.fields: list[GamePiece] = [None for _ in range(
            self.board_height*self.board_width+1)]  # Plus one because staring from 1

    def start_game(self):
        self.init_pieces()
        self.game_state = GameState.LIGHT_TURN

    def row_col2field_no(self, row: int, col: int) -> int:
        return row * self.board_width + col + 1

    def field_no2row_col(self, field_no: int) -> tuple[int]:
        # self.board_width, (field_no-1) % self.board_width
        return (field_no-1)

    def get_piece_color(self, field_no: int) -> GamePieceColor:
        if field_no >= 1 and field_no <= 32:
            return self.fields[field_no].get_color()
        else:
            return GamePieceColor.ERROR

    def get_piece_color_rc(self, row: int, col: int) -> GamePieceColor:
        return self.get_piece_color(self.row_col2field_no(row, col))

    def init_pieces(self) -> None:
        for i in range(1, 13):
            self.fields[i] = GamePiece(
                GamePieceColor.DARK, GamePieceType.MAN, i)
            self.fields[i+20] = GamePiece(
                GamePieceColor.LIGHT, GamePieceType.MAN, i+20)
        self.debug_print_board()

    def debug_print_board(self) -> None:
        board_repr = []
        for row in range(self.board_height-1, -1, -1):
            if row % 2 != 0:
                board_repr.append('  ')
            for col in range(self.board_width-1, -1, -1):
                i = row * self.board_width + col + 1
                if self.fields[i] is None:
                    board_repr.append('..')
                else:
                    if self.fields[i].get_color() == GamePieceColor.LIGHT:
                        board_repr.append('L')
                    else:
                        board_repr.append('D')
                    if self.fields[i].type == GamePieceType.MAN:
                        board_repr.append('M')
                    else:
                        board_repr.append('K')
                board_repr.append('  ')
            board_repr.append('\n')
        board_repr.append('\n')
        print(''.join(board_repr))

    def filter_pieces(self) -> list[GamePiece]:
        return list(filter(lambda x: x is not None, self.fields))

    def move_piece(self, from_field, to_field) -> MoveResult:
        if from_field < 1 or from_field > 32:
            return MoveResult(GameError.CANT_MOVE_PIECE)
        if to_field < 1 or to_field > 32:
            return MoveResult(GameError.ILLEGAL_MOVE)
        piece = self.fields[from_field]
        if piece is None:
            return MoveResult(GameError.CANT_MOVE_PIECE)
        if self.fields[to_field] is not None:
            return MoveResult(GameError.FIELD_TAKEN)
        # Check if it's this player's turn
        if piece.get_color() == GamePieceColor.LIGHT and self.game_state != GameState.LIGHT_TURN:
            return MoveResult(GameError.NOT_YOUR_TURN)
        if piece.get_color() == GamePieceColor.DARK and self.game_state != GameState.DARK_TURN:
            return MoveResult(GameError.NOT_YOUR_TURN)
        from_row, from_col = self.field_no2row_col(from_field)
        to_row, to_col = self.field_no2row_col(to_field)
        up_down = Direction.UP if to_row > from_row else Direction.DOWN
        field_count = abs(to_row - from_row)
        if field_count > 2:
            return MoveResult(GameError.ILLEGAL_MOVE)
        if from_row % 2 == 0:
            left_right = Direction.LEFT if to_col > from_col else Direction.RIGHT
        else:
            left_right = Direction.LEFT if to_col >= from_col else Direction.RIGHT
        # Check if the piece is moving backwards and if it is check if it's a king
        if up_down == Direction.UP and piece.get_color() == GamePieceColor.LIGHT and piece.get_type() == GamePieceType.MAN:
            return MoveResult(GameError.NOT_KING)
        if up_down == Direction.DOWN and piece.get_color() == GamePieceColor.DARK and piece.get_type() == GamePieceType.MAN:
            return MoveResult(GameError.NO_KING)
        # Calculate the position of the piece that will be captured
        through_row = from_row
        through_col = from_col
        through_field = None
        if field_count == 2:
            if from_row % 2 == 0:
                through_row += (1 if up_down == Direction.UP else -1)
                through_col += (1 if left_right == Direction.LEFT else 0)
            else:
                through_row += (1 if up_down == Direction.UP else -1)
                through_col += (0 if left_right == Direction.LEFT else -1)
            through_field = self.row_col2field_no(through_row, through_col)
            if through_field is None:
                return MoveResult(GameError.ILLEGAL_MOVE)
            # Check if player tried to capture his own piece
            if piece.get_color() == self.fields[through_field].get_color():
                return MoveResult(GameError.ILLEGAL_MOVE)
        # Move the piece
        self.fields[to_field] = piece
        self.fields[from_field] = None
        self.debug_print_board()
        if field_count == 2:
            self.fields[through_field] = None
            return MoveResult(GameError.NO_ERROR, end_turn=not self.can_piece_make_any_move(self, to_field), captured_piece_field=through_field)
        return MoveResult(GameError.NO_ERROR, end_turn=True)

    def can_piece_make_any_move(self, from_field: int) -> bool:
        piece = self.fields[from_field]
        opponent_color = GamePieceColor.LIGHT if piece.get_color(
        ) == GamePieceColor.DARK else GamePieceColor.DARK
        from_row, from_col = self.field_no2row_col(from_field)
        if piece.get_color() == GamePieceColor.DARK or piece.get_type() == GamePieceType.KING:
            if from_row % 2 == 0:
                # One up left
                if self.get_piece_color_rc(from_row+1, from_col+1) is None:
                    return True
                # One up right
                if self.get_piece_color_rc(from_row+1, from_col) is None:
                    return True
                # Two up left
                if self.get_piece_color_rc(from_row+2, from_col+1) is None \
                        and self.get_piece_color_rc(from_row+1, from_col+1) == opponent_color:
                    return True
                # Two up right
                if self.get_piece_color_rc(from_row+2, from_col-1) is None \
                        and self.get_piece_color_rc(from_row+1, from_col) == opponent_color:
                    return True
            else:
                # One up left
                if self.get_piece_color_rc(from_row+1, from_col) is None:
                    return True
                # One up right
                if self.get_piece_color_rc(from_row+1, from_col-1) is None:
                    return True
                # Two up left
                if self.get_piece_color_rc(from_row+2, from_col+1) is None \
                        and self.get_piece_color_rc(from_row+1, from_col) == opponent_color:
                    return True
                # Two up right
                if self.get_piece_color_rc(from_row+2, from_col-1) is None \
                        and self.get_piece_color_rc(from_row+1, from_col-1) == opponent_color:
                    return True

        if piece.get_color() == GamePieceColor.LIGHT or piece.get_type() == GamePieceType.KING:
            if from_row % 2 == 0:
                # One down left
                if self.get_piece_color_rc(from_row-1, from_col+1) is None:
                    return True
                # One down right
                if self.get_piece_color_rc(from_row-1, from_col) is None:
                    return True
                # Two down left
                if self.get_piece_color_rc(from_row-2, from_col+1) is None \
                        and self.get_piece_color_rc(from_row-1, from_col+1) == opponent_color:
                    return True
                # Two down right
                if self.get_piece_color_rc(from_row-2, from_col-1) is None \
                        and self.get_piece_color_rc(from_row-1, from_col) == opponent_color:
                    return True
            else:
                # One down left
                if self.get_piece_color_rc(from_row-1, from_col) is None:
                    return True
                # One down right
                if self.get_piece_color_rc(from_row-1, from_col-1) is None:
                    return True
                # Two down left
                if self.get_piece_color_rc(from_row-2, from_col+1) is None \
                        and self.get_piece_color_rc(from_row-1, from_col) == opponent_color:
                    return True
                # Two down right
                if self.get_piece_color_rc(from_row-2, from_col-1) is None \
                        and self.get_piece_color_rc(from_row - 1, from_col - 1) == opponent_color:
                    return True
