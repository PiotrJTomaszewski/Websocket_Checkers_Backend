from checkers.messages import MessageType, encode_piece_list
from typing import List, Optional
from checkers.game.games_handler import GamesHandler
from checkers.game import player

import tornado.websocket
import struct


class PlayerHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.player: 'player.Player' = None
        self.msg_send_lookup = {
            MessageType.WELCOME: self.msg_encode_welcome,
            MessageType.WELCOME_NEW: self.msg_encode_welcome_new,
            MessageType.START_GAME: self.msg_encode_start_game,
            MessageType.CURRENT_STATE: self.msg_encode_current_state,
            MessageType.WRONG_MOVE: self.msg_encode_wrong_move,
            MessageType.MOVE_OK: self.msg_encode_move_ok,
            MessageType.GAME_END: self.msg_encode_game_end
        }

    def check_origin(self, origin) -> bool:
        # HTML for the game is hosted on a different server
        return True

    def open(self) -> None:
        print("New Connection")

    def select_subprotocol(self, subprotocols: List[str]) -> Optional[str]:
        if "checkers_game" in subprotocols:
            return "checkers_game"
        return None

    def msg_encode_welcome(self, data: dict = None) -> bytes:
        return struct.pack('!B', MessageType.WELCOME.value)

    def msg_encode_welcome_new(self, data: dict = None) -> bytes:
        uuid_str: str = data['uuid_str']
        return b''.join((struct.pack('!B', MessageType.WELCOME_NEW.value), uuid_str.encode('utf-8')))

    def msg_encode_start_game(self, data: dict = None) -> bytes:
        return struct.pack('!BB', MessageType.START_GAME.value, data['piece_color'].value)

    def msg_encode_current_state(self, data: dict = None) -> bytes:
        return b''.join((struct.pack('!BBB', MessageType.CURRENT_STATE.value, data['piece_color'].value, data['game_state'].value), encode_piece_list(data['pieces'])))

    def msg_encode_wrong_move(self, data: dict = None) -> bytes:
        return struct.pack('!BBB', MessageType.WRONG_MOVE.value, data['from_field'], data['error'].value)

    def msg_encode_move_ok(self, data: dict = None) -> bytes:
        return struct.pack('!BBB??B', MessageType.MOVE_OK.value, data['from_field'], data['to_field'], data['end_turn'], data['promote'], data.get('captured_field') or 0)

    def msg_encode_game_end(self, data: dict = None) -> bytes:
        return struct.pack('!BB', MessageType.GAME_END.value, data['game_state'].value)

    def msg_send(self, msg_type: MessageType, data: dict = None) -> None:
        print(f'Message {msg_type.name} sent to {self.player.get_uuid_str()}')
        self.write_message(self.msg_send_lookup[msg_type](data), binary=True)

    def msg_recv_join_new(self) -> None:
        self.player, _ = GamesHandler().add_player(None)
        self.player.set_send_msg_func(self.msg_send)
        self.player.mark_connected()
        print("Received JOIN_NEW")
        self.msg_send(MessageType.WELCOME_NEW,
            {'uuid_str': self.player.get_uuid_str()})
        GamesHandler().check_and_start_game(self.player.room)

    def msg_recv_join_existing(self, encoded_data: bytes) -> None:
        uuid_str = encoded_data.decode('utf-8')
        self.player, is_new = GamesHandler().add_player(uuid_str)
        self.player.set_send_msg_func(self.msg_send)
        self.player.mark_connected()
        print(f"Received JOIN_EXISTING from {uuid_str}")
        if is_new:
            self.msg_send(MessageType.WELCOME)
            GamesHandler().check_and_start_game(self.player.room)
        else:
            GamesHandler().send_state(self.player)

    def msg_recv_move(self, encoded_data: bytes) -> None:
        from_field, to_field = struct.unpack('!BB', encoded_data)
        print(f"Received MOVE from {self.player.get_uuid_str()} from {from_field} to {to_field}")
        GamesHandler().move_piece(self.player, from_field, to_field)

    def on_message(self, message: bytes) -> None:
        msg_type = MessageType(struct.unpack('!B', bytes((message[0], )))[0])
        if msg_type == MessageType.JOIN_NEW:
            self.msg_recv_join_new()
        elif msg_type == MessageType.JOIN_EXISTING:
            self.msg_recv_join_existing(message[1:])
        elif msg_type == MessageType.MOVE:
            self.msg_recv_move(message[1:])
        else:
            print(f"Received incorrect message type {msg_type.name}")

    def on_close(self) -> None:
        print("Connection closed")
        if self.player is not None:
            self.player.mark_disconnected()
            if not self.player.room.in_game:
                GamesHandler().remove_room(self.player.room)
                print("Player has left, he/she wasn't in a game so removing his/her room")
