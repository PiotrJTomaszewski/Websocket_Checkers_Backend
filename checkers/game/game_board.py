from .game_piece import GamePiece, GamePieceColor, GamePieceType


class GameBoard:
    width = 4
    height = 8

    def __init__(self) -> None:
        self.fields: list[list[GamePiece]] = [
            [None for _ in range(self.width)] for _ in range(self.height)]

    def row_col2field_no(self, row: int, col: int):
        return row * self.width + col + 1

    def init_pieces(self) -> None:
        for col in range(self.width):
            for row in range(0, 3):
                self.fields[row][col] = GamePiece(
                    GamePieceColor.DARK, GamePieceType.MAN, self.row_col2field_no(row, col))
            for row in range(5, 8):
                self.fields[row][col] = GamePiece(
                    GamePieceColor.LIGHT, GamePieceType.MAN, self.row_col2field_no(row, col))
        self.debug_print_board()

    def debug_print_board(self) -> None:
        board_repr = []
        for row in range(self.height-1, -1, -1):
            if row % 2 != 0:
                board_repr.append('  ')
            for col in range(self.width-1, -1, -1):
                if self.fields[row][col] is None:
                    board_repr.append('..')
                else:
                    if self.fields[row][col].get_color() == GamePieceColor.LIGHT:
                        board_repr.append('L')
                    else:
                        board_repr.append('D')
                    if self.fields[row][col].type == GamePieceType.MAN:
                        board_repr.append('M')
                    else:
                        board_repr.append('K')
                board_repr.append('  ')
            board_repr.append('\n')
        board_repr.append('\n')
        print(''.join(board_repr))

    def flatten_pieces(self) -> list[GamePiece]:
        return list(filter(lambda x: x is not None, [piece for sublist in self.fields for piece in sublist]))