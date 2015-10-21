# *-* coding:utf-8 *-*
import json
import logging
import signal
import time

from collections import defaultdict
from urllib.parse import urlparse

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_command_line, options
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler, WebSocketClosedError

define('debug', default=False, type=bool, help='Run in debug mode')
define('port', default=8088, type=int, help='Server port')
define('allowed_hosts', default="localhost:8088", multiple=True, help='Allowed hosts for cross domain connections')

class SprintHandler(WebSocketHandler):
    '''Trata atualizações de tempo real no quadro de tarefas'''

    def check_origin(self, origin):
        allowed = super().check_origin(origin)
        parsed = urlparse(origin.lower())
        matched = any(parsed.netloc == host for host in options.allowed_hosts)
        return options.debug or allowed or matched

    def open(self, sprint):
        '''Registra-se para receber atualizações de sprint em uma nova camada'''
        self.sprint = sprint
        self.application.add_subscriber(self.sprint, self)

    def on_message(self, message):
        '''Faz o broadcast das atualizações para outros clientes interessados'''
        self.application.broadcast(message, channel=self.sprint, sender=self)

    def on_close(self):
        '''Remove registros'''
        self.application.remove_subscriber(self.sprint, self)

class UpdateHandler(RequestHandler):
    '''Trata atualizações de aplicação Django'''

    def post(self, model, pk):
        self._broadcast(model, pk, 'add')

    def put(self, model, pk):
        self._broadcast(model, pk, 'update')

    def delete(self, model, pk):
        self._broadcast(model, pk, 'remove')

    def _broadcast(self, model, pk, action):
        message = json.dumps({
            'model': model,
            'id': pk,
            'action': action,
        })
        self.application.broadcast(message)
        self.write("Ok")

class ScrumApplication(Application):
    'Minha applicação'
    def __init__(self, **kwargs):
        routes = [
            (r'/(?P<sprint>[0-9]+)', SprintHandler),
            (r'/(?P<model>task|sprint|user)/(?P<pk>[0-9]+)', UpdateHandler),
        ]
        super().__init__(routes, **kwargs)
        self.subscriptions = defaultdict(list)

    def add_subscriber(self, channel, subscriber):
        self.subscriptions[channel].append(subscriber)

    def remove_subscriber(self, channel, subscriber):
        self.subscriptions[channel].remove(subscriber)

    def get_subscribers(self, channel):
        return self.subscriptions[channel]

    def broadcast(self, message, channel=None, sender=None):
        if channel is None:
            for c in self.subscriptions.keys():
                self.broadcast(message, channel=c, sender=sender)
        else:
            peers = self.get_subscribers(channel)
            for peer in peers:
                if peer != sender:
                    try:
                        peer.write_message(message)
                    except WebSocketClosedError:
                        self.remove_subscriber(channel, peer)

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
    application = ScrumApplication()
    server = HTTPServer(application)
    server.listen(options.port)
    signal.signal(signal.SIGINT, lambda sig, frame: shutdown(server) )
    logging.info('Starting server on localhost:{}'.format(options.port))
    IOLoop.instance().start()
