from checkers.game.game import Game
from checkers.game.games_handler import GamesHandler
from checkers.game import player

import tornado.websocket


class PlayerHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.player: 'player.Player' = None

    def check_origin(self, origin) -> bool:
        # HTML for the game is hosted on a different server
        return True

    def open(self) -> None:
        print("New Connection")

    def msg_send(self, msg_type, data=None):
        print('Message sent: ', msg_type, data)
        if data is None:
            self.write_message(msg_type)
        else:
            self.write_message(';'.join([msg_type, ';'.join(data)]))

    def msg_hand_join_new(self, data=None):
        self.player, _ = GamesHandler().add_player(None)
        self.player.set_send_msg_func(self.msg_send)
        self.msg_send('WelcomeNew', [self.player.get_uuid_str()])
        GamesHandler().check_and_start_game(self.player.room)

    def msg_hand_join_existing(self, data=None):
        uuid_str = data[0]
        self.player, is_new = GamesHandler().add_player(uuid_str)
        self.player.set_send_msg_func(self.msg_send)
        if is_new:
            self.msg_send('Welcome')
            GamesHandler().check_and_start_game(self.player.room)
        else:
            GamesHandler().send_state(self.player)

    def msg_hand_move(self, data=None):
        from_field = int(data[0])
        to_field = int(data[1])
        GamesHandler().move_piece(self.player, from_field, to_field)

    def on_message(self, message):
        print(f"Message received: {message}")
        # TODO: Use dict and message type as number
        tmp = message.split(';')
        if tmp[0] == 'JoinNew':
            self.msg_hand_join_new()
        elif tmp[0] == 'JoinExisting':
            self.msg_hand_join_existing(tmp[1:])
        elif tmp[0] == 'Move':
            self.msg_hand_move(tmp[1:])

    def on_close(self):
        print("Connection closed")
        # TODO: Cleanup if both players left the room

    def on_connection_close(self) -> None:
        print("On connection close")

