from typing import List, Tuple
from checkers.game.game_piece import GamePiece, GamePieceColor, GamePieceType
from enum import Enum


class GameState(Enum):
    NOT_STARTED = 1
    LIGHT_TURN = 2
    DARK_TURN = 3
    LIGHT_WON = 4
    DARK_WON = 5
    TIE = 6


class MoveError(Enum):
    NO_ERROR = 1
    CANT_MOVE_PIECE = 2
    ILLEGAL_MOVE = 3
    FIELD_TAKEN = 4
    NOT_KING = 5
    NOT_YOUR_TURN = 6
    NOT_YOUR_PIECE = 7
    MUST_CAPTURE = 8
    MUST_USE_SAME_PIECE = 9


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class MoveResult:
    def __init__(self, move_error: MoveError, end_turn: bool = None, promote: bool = None, captured_piece_field: int = None) -> None:
        self.move_error = move_error
        self.end_turn = end_turn
        self.promote = promote
        self.captured_piece_field = captured_piece_field


class Game:
    board_width = 4
    board_height = 8

    def __init__(self) -> None:
        self.game_state: GameState = GameState.NOT_STARTED
        self.move_error: MoveError = MoveError.NO_ERROR
        self.fields: List[GamePiece] = [None for _ in range(
            self.board_height*self.board_width+1)]  # Plus one because staring from 1
        self.continue_capturing_field_no = None

    def start_game(self) -> None:
        self.init_pieces()
        self.game_state = GameState.LIGHT_TURN

    def row_col2field_no(self, row: int, col: int) -> int:
        return row * self.board_width + col + 1

    def field_no2row_col(self, field_no: int) -> Tuple[int]:
        # self.board_width, (field_no-1) % self.board_width
        return (field_no-1) // self.board_width, (field_no-1) % self.board_width

    def get_piece_color(self, field_no: int) -> GamePieceColor:
        if field_no >= 1 and field_no <= 32:
            if self.fields[field_no] is not None:
                return self.fields[field_no].get_color()
            return GamePieceColor.NOCOLOR
        else:
            return GamePieceColor.ERROR

    def get_piece_color_rc(self, row: int, col: int) -> GamePieceColor:
        if row >= 0 and row < self.board_height and col >= 0 and col < self.board_width:
            return self.get_piece_color(self.row_col2field_no(row, col))
        return GamePieceColor.ERROR

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
        # self.debug_print_board_numbers()

    def debug_print_board_numbers(self) -> None:
        board_repr = []
        for row in range(self.board_height-1, -1, -1):
            if row % 2 != 0:
                board_repr.append('  ')
            for col in range(self.board_width-1, -1, -1):
                i = row * self.board_width + col + 1
                if self.fields[i] is None:
                    board_repr.append('..')
                else:
                    if self.fields[i].field_no < 10:
                        board_repr.append('0')
                    board_repr.append(f'{self.fields[i].field_no}')
                board_repr.append('  ')
            board_repr.append('\n')
        board_repr.append('\n')
        print(''.join(board_repr))

    def filter_pieces(self) -> List[GamePiece]:
        return list(filter(lambda x: x is not None, self.fields))

    def check_and_promote_piece(self, field_no: int) -> bool:
        piece = self.fields[field_no]
        if piece is not None and piece.get_type() == GamePieceType.MAN:
            row = (field_no-1) // self.board_width
            if piece.get_color() == GamePieceColor.LIGHT and row == 0:
                piece.type = GamePieceType.KING
                return True
            if piece.get_color() == GamePieceColor.DARK and row == self.board_height-1:
                piece.type = GamePieceType.KING
                return True
        return False

    def move_piece(self, from_field: int, to_field: int) -> MoveResult:
        if self.continue_capturing_field_no is not None and from_field != self.continue_capturing_field_no:
            return MoveResult(MoveError.MUST_USE_SAME_PIECE)
        if from_field < 1 or from_field > 32:
            return MoveResult(MoveError.CANT_MOVE_PIECE)
        if to_field < 1 or to_field > 32:
            return MoveResult(MoveError.ILLEGAL_MOVE)
        piece = self.fields[from_field]
        if piece is None:
            return MoveResult(MoveError.CANT_MOVE_PIECE)
        if self.fields[to_field] is not None:
            return MoveResult(MoveError.FIELD_TAKEN)
        # Check if it's this player's turn
        if piece.get_color() == GamePieceColor.LIGHT and self.game_state != GameState.LIGHT_TURN:
            return MoveResult(MoveError.NOT_YOUR_TURN)
        if piece.get_color() == GamePieceColor.DARK and self.game_state != GameState.DARK_TURN:
            return MoveResult(MoveError.NOT_YOUR_TURN)
        from_row, from_col = self.field_no2row_col(from_field)
        to_row, to_col = self.field_no2row_col(to_field)
        up_down = Direction.UP if to_row > from_row else Direction.DOWN
        field_count = abs(to_row - from_row)
        if field_count > 2:
            return MoveResult(MoveError.ILLEGAL_MOVE)
        if from_row % 2 == 0:
            left_right = Direction.LEFT if to_col > from_col else Direction.RIGHT
        else:
            left_right = Direction.LEFT if to_col >= from_col else Direction.RIGHT
        # Check if the piece is moving backwards and if it is check if it's a king
        if up_down == Direction.UP and piece.get_color() == GamePieceColor.LIGHT and piece.get_type() == GamePieceType.MAN:
            return MoveResult(MoveError.NOT_KING)
        if up_down == Direction.DOWN and piece.get_color() == GamePieceColor.DARK and piece.get_type() == GamePieceType.MAN:
            return MoveResult(MoveError.NOT_KING)
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
            if through_field is None or self.fields[through_field] is None:
                return MoveResult(MoveError.ILLEGAL_MOVE)
            # Check if player tried to capture his own piece
            if piece.get_color() == self.fields[through_field].get_color():
                return MoveResult(MoveError.ILLEGAL_MOVE)
        else:
            if self.can_capture_any(from_field):
                return MoveResult(MoveError.MUST_CAPTURE)
        # Move the piece
        self.fields[to_field] = piece
        piece.field_no = to_field
        self.fields[from_field] = None
        if field_count == 2:
            self.fields[through_field] = None
            end_turn = not self.can_capture_any(to_field)
            if end_turn:
                self.continue_capturing_field_no = None
                if self.game_state == GameState.LIGHT_TURN:
                    self.game_state = GameState.DARK_TURN
                else:
                    self.game_state = GameState.LIGHT_TURN
            else:
                self.continue_capturing_field_no = to_field
            promote = self.check_and_promote_piece(to_field)
            self.debug_print_board()
            return MoveResult(MoveError.NO_ERROR, end_turn=end_turn, promote=promote, captured_piece_field=through_field)
        if self.game_state == GameState.LIGHT_TURN:
            self.game_state = GameState.DARK_TURN
        else:
            self.game_state = GameState.LIGHT_TURN
        promote = self.check_and_promote_piece(to_field)
        self.continue_capturing_field_no = None
        self.debug_print_board()
        return MoveResult(MoveError.NO_ERROR, end_turn=True, promote=promote)

    def can_capture_any(self, from_field: int) -> bool:
        piece = self.fields[from_field]
        opponent_color = \
            GamePieceColor.LIGHT if piece.get_color() == GamePieceColor.DARK else GamePieceColor.DARK
        from_row, from_col = self.field_no2row_col(from_field)
        if piece.get_color() == GamePieceColor.DARK or piece.get_type() == GamePieceType.KING:
            if from_row % 2 == 0:
                # Two up left
                if self.get_piece_color_rc(from_row+2, from_col+1) == GamePieceColor.NOCOLOR \
                        and self.get_piece_color_rc(from_row+1, from_col+1) == opponent_color:
                    # print("Two up left")
                    return True
                # Two up right
                if self.get_piece_color_rc(from_row+2, from_col-1) == GamePieceColor.NOCOLOR \
                        and self.get_piece_color_rc(from_row+1, from_col) == opponent_color:
                    # print("Two up right")
                    return True
            else:
                # Two up left
                if self.get_piece_color_rc(from_row+2, from_col+1) == GamePieceColor.NOCOLOR \
                        and self.get_piece_color_rc(from_row+1, from_col) == opponent_color:
                    # print("Two up left")
                    return True
                # Two up right
                if self.get_piece_color_rc(from_row+2, from_col-1) == GamePieceColor.NOCOLOR \
                        and self.get_piece_color_rc(from_row+1, from_col-1) == opponent_color:
                    # print("Two up right")
                    return True

        if piece.get_color() == GamePieceColor.LIGHT or piece.get_type() == GamePieceType.KING:
            if from_row % 2 == 0:
                # Two down left
                if self.get_piece_color_rc(from_row-2, from_col+1) == GamePieceColor.NOCOLOR \
                        and self.get_piece_color_rc(from_row-1, from_col+1) == opponent_color:
                    # print("Two down left")
                    return True
                # Two down right
                if self.get_piece_color_rc(from_row-2, from_col-1) == GamePieceColor.NOCOLOR \
                        and self.get_piece_color_rc(from_row-1, from_col) == opponent_color:
                    # print("Two down right")
                    return True
            else:
                # Two down left
                if self.get_piece_color_rc(from_row-2, from_col+1) == GamePieceColor.NOCOLOR \
                        and self.get_piece_color_rc(from_row-1, from_col) == opponent_color:
                    # print("Two down left")
                    return True
                # Two down right
                if self.get_piece_color_rc(from_row-2, from_col-1) == GamePieceColor.NOCOLOR \
                        and self.get_piece_color_rc(from_row - 1, from_col - 1) == opponent_color:
                    # print("Two down right")
                    return True
        return False

    def can_piece_make_any_move(self, from_field: int) -> bool:
        piece = self.fields[from_field]
        from_row, from_col = self.field_no2row_col(from_field)
        if piece.get_color() == GamePieceColor.DARK or piece.get_type() == GamePieceType.KING:
            if from_row % 2 == 0:
                # One up left
                if self.get_piece_color_rc(from_row+1, from_col+1) == GamePieceColor.NOCOLOR:
                    # print("One up left")
                    return True
                # One up right
                if self.get_piece_color_rc(from_row+1, from_col) == GamePieceColor.NOCOLOR:
                    # print("One up right")
                    return True
            else:
                # One up left
                if self.get_piece_color_rc(from_row+1, from_col) == GamePieceColor.NOCOLOR:
                    # print("One up left")
                    return True
                # One up right
                if self.get_piece_color_rc(from_row+1, from_col-1) == GamePieceColor.NOCOLOR:
                    # print("One up right")
                    return True

        if piece.get_color() == GamePieceColor.LIGHT or piece.get_type() == GamePieceType.KING:
            if from_row % 2 == 0:
                # One down left
                if self.get_piece_color_rc(from_row-1, from_col+1) == GamePieceColor.NOCOLOR:
                    # print("One down left")
                    return True
                # One down right
                if self.get_piece_color_rc(from_row-1, from_col) == GamePieceColor.NOCOLOR:
                    # print("One down right")
                    return True
            else:
                # One down left
                if self.get_piece_color_rc(from_row-1, from_col) == GamePieceColor.NOCOLOR:
                    # print("One down left")
                    return True
                # One down right
                if self.get_piece_color_rc(from_row-1, from_col-1) == GamePieceColor.NOCOLOR:
                    # print("One down right")
                    return True
        return self.can_capture_any(from_field)

    def check_victory(self) -> bool:
        light_pieces_count = 0
        dark_pieces_count = 0
        light_pieces_that_can_move = 0
        dark_pieces_that_can_move = 0
        for piece in self.fields:
            if piece is not None:
                if piece.get_color() == GamePieceColor.LIGHT:
                    light_pieces_count += 1
                    if self.can_piece_make_any_move(piece.field_no):
                        light_pieces_that_can_move += 1
                else:
                    dark_pieces_count += 1
                    if self.can_piece_make_any_move(piece.field_no):
                        dark_pieces_that_can_move += 1
        if light_pieces_that_can_move == 0 and dark_pieces_that_can_move == 0:
            self.game_state = GameState.TIE
            return True
        if light_pieces_count == 0 or light_pieces_that_can_move == 0:
            self.game_state = GameState.DARK_WON
            return True
        if dark_pieces_count == 0 or dark_pieces_that_can_move == 0:
            self.game_state = GameState.LIGHT_WON
            return True
        return False
