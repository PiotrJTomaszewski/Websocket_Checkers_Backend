from checkers.game.games_handler import GamesHandler
from uuid import UUID, uuid4
import tornado.websocket


class PlayerHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.player = None

    def check_origin(self, origin) -> bool:
        # HTML for the game is hosted on a different server
        return True

    def open(self) -> None:
        print("New Connection")

    def msg_hand_join_new(self, data=None):
        self.player = GamesHandler().add_player(None)
        self.write_message(f'WelcomeNew;{self.player.get_uuid_str()}')

    def msg_hand_join_existing(self, data=None):
        uuid_str = data[0]
        self.player = GamesHandler().add_player(uuid_str)
        self.write_message('Welcome')

    def on_message(self, message):
        print(f"Message received: {message}")
        # TODO: Use dict and message type as number
        tmp = message.split(';')
        if tmp[0] == 'JoinNew':
            self.msg_hand_join_new()
        elif tmp[0] == 'JoinExisting':
            self.msg_hand_join_existing(tmp[1:])



    def on_close(self):
        print("Connection closed")
