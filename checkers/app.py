from checkers.game.games_handler import GamesHandler
from checkers.game.game import GameState
from .player_handler import PlayerHandler
import tornado.ioloop
import tornado.websocket
import tornado.httpserver


application = tornado.web.Application([
    (r'/ws', PlayerHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    print("Server ready")
    tornado.ioloop.PeriodicCallback(GamesHandler().check_and_remove_inactive, 30 * 60 * 1000).start()
    tornado.ioloop.IOLoop.instance().start()
