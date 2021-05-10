from . import player, game


class GameRoom:
    def __init__(self) -> None:
        self.players: list['player.Player'] = [None, None]
        self.game: 'game.Game' = None
        self.in_game = False

    def is_full(self):
        return self.players[0] is not None and self.players[1] is not None

    def add_player(self, player: 'player.Player') -> int:
        if self.players[0] is None:
            self.players[0] = player
            return 0
        else:
            self.players[1] = player
            return 1
