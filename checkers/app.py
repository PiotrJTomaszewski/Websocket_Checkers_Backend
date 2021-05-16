from checkers.game.games_handler import GamesHandler
from checkers.game.game import GameState
from .player_handler import PlayerHandler
import tornado.ioloop
import tornado.websocket
import tornado.httpserver
import tornado.netutil
from tornado.options import options, define

define('listen_port', group='webserver', default=8888, help='Listen port')
define('unix_socket', group='webserver', default=None, help='Path to unix socket to bind')

application = tornado.web.Application([
    (r'/ws', PlayerHandler),
])

if __name__ == '__main__':
    options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application)
    if options.unix_socket:
        socket = tornado.netutil.bind_unix_socket(options.unix_socket)
        http_server.add_socket(socket)
    else:
        http_server.listen(options.listen_port)
    print("Server ready")
    tornado.ioloop.PeriodicCallback(GamesHandler().check_and_remove_inactive, 30 * 60 * 1000).start()
    tornado.ioloop.IOLoop.instance().start()
