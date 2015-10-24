# *-* coding:utf-8 *-*
import json
import logging
import signal
import time
import uuid
import os

from collections import defaultdict
from urllib.parse import urlparse


from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_command_line, options
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler, WebSocketClosedError

from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

from redis import Redis
from tornadoredis import Client
from tornadoredis.pubsub import BaseSubscriber

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
        self.sprint = None
        channel = self.get_argument('channel', None)
        if not channel:
            self.close()
        else:
            try:
                self.sprint = self.application.signer.unsign(channel, max_age=60 * 30)
            except (BadSignature, SignatureExpired):
                self.close()
            else:
                self.uid = uuid.uuid4().hex
                self.application.add_subscriber(self.sprint, self)

    def on_message(self, message):
        '''Faz o broadcast das atualizações para outros clientes interessados'''
        if self.sprint is not None:
            self.application.broadcast(message, channel=self.sprint, sender=self)

    def on_close(self):
        '''Remove registros'''
        if self.sprint is not None:
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
        logging.info('JSON: %s' %(message) )
        self.application.broadcast(message)
        self.write("Ok")


class RedisSubscriber(BaseSubscriber):

    def on_message(self, msg):
        '''Trata nova mensagem no canal Redis.'''
        if msg and msg.king == 'menssage':
            try:
                message = json.loads(msg.body)
                sender = message['sender']
                message = message['message']
            except (ValueError, KeyError):
                message = msg.body
                sender = None
            subscribers = list(self.subscribers[msg.channel].keys())
            for subscriber in subscribers:
                if sender is None or sender != subscriber.uid:
                    try:
                        subscriber.write_message(msg.body)
                    except WebSocketClosedError:
                        self.unsubscribe(msg.channel, subscriber)
        super().on_message(msg)

class ScrumApplication(Application):
    'Minha applicação'
    def __init__(self, **kwargs):
        routes = [
            (r'/socket', SprintHandler),
            (r'/(?P<model>task|sprint|user)/(?P<pk>[0-9]+)', UpdateHandler),
        ]
        super().__init__(routes, **kwargs)
        self.subscriber = RedisSubscriber(Client())
        self.publisher = Redis()
        self._key = os.environ.get('WATERCOOLER_SECRET', '3121556214dsa654d6asdas')
        self.signer = TimestampSigner(self._key)

    def add_subscriber(self, channel, subscriber):
        self.subscriber.subscribe([ 'all', channel ], subscriber)

    def remove_subscriber(self, channel, subscriber):
        self.subscriber.unsubscribe(channel, subscriber)
        self.subscriber.unsubscribe('all', subscriber)

    def broadcast(self, message, channel=None, sender=None):
        channel = 'all' if channel is None else channel
        message = json.dumps({
            'sender': sender and sender.uid,
            'message': message
        })
        self.publisher.publish(channel, message)

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
