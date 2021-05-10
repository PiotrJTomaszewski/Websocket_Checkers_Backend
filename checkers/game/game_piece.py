from enum import Enum


class GamePieceColor(Enum):
    ERROR = 0
    LIGHT = 1
    DARK = 2


class GamePieceType(Enum):
    MAN = 1
    KING = 2


class GamePiece:
    def __init__(self, color: GamePieceColor, type: GamePieceType, field_no: int) -> None:
        self.color = color
        self.type = type
        self.field_no = field_no

    def get_color(self) -> GamePieceColor:
        return self.color

    def get_type(self) -> GamePieceType:
        return self.type

    def get_field_no(self) -> int:
        return self.field_no

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'{self.color.name} {self.type.name} at {self.field_no}'
