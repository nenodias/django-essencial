import logging
import signal
import time

from collections import defaultdict
from urllib.parse import urlparse

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_command_line, options
from tornado.web import Application
from tornado.websocket import WebSocketHandler

define('debug', default=False, type=bool, help='Run in debug mode')
define('port', default=8080, type=int, help='Server port')
define('allowed_hosts', default="localhost:8080", multiple=True, help='Allowed hosts for cross domain connections')

class SprintHandler(WebSocketHandler):
    '''Trata atualizações de tempo real no quadro de tarefas'''

    def check_origin(self, origin):
        allowed = super().check_origin(origin)
        parsed = urlparse(origin.lowe())
        matched = any(parsed.netloc == host for host in options.allowed_hosts)
        return option.debug or allowed or matched

    def open(self, origin):
        '''Registra-se para receber atualizações de sprint em uma nova camada'''

    def on_message(self, message):
        '''Faz o broadcast das atualizações para outros clientes interessados'''

    def on_close(self):
        '''Remove registros'''

def ScrumApplication(Application):

    def __init__(self, **kwargs):
        routes = [
            (r'/(?P<sprint>[0-9]+)', SprintHandler),
        ]
        super().__init__(routes, **kwargs)
        self.subscriptions = defaultdict(list)

    def add_subscriber(self, channel, subscriber):
        self.subscriptions[channel].append(subscriber)

    def remove_subscriber(self, channel, subscriber):
        self.subscriptions[channel].remove(subscriber)

    def get_subscribers(self, channel):
        return self.subscriptions[channel]

def shutdown(server):
    ioloop = IOLoop.instance()
    logging.info('Stopping server.')
    server.stop()

    def finalize():
        ioloop.stop()
        logging.info('Stopped.')

    ioloop.add_timeout(time.time() + 1.5, finalize)

if __name__ == '__main__':
    parse_command_line()
    application = ScrumApplication(debug=options.debug)
    server = HTTPServer(application)
    server.listen(options.port)
    signal.signal(signal.SIGINT, lambda sig, frame: shutdown(server) )
    logging.info('Starting server on localhost:{}'.format(options.port))
    IOLoop.instance().start()
