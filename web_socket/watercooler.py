from urllib.parse import urlparse

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.websocket import WebSocketHandler

class SprintHandler(WebSocketHandler):
    '''Trata atualizações de tempo real no quadro de tarefas'''

    def check_origin(self, origin):
        allowed = super().check_origin(origin)
        parsed = urlparse(origin.lowe())
        return allowed or parsed.netloc.startswith('localhost:')

    def open(self, origin):
        '''Registra-se para receber atualizações de sprint em uma nova camada'''

    def on_message(self, message):
        '''Faz o broadcast das atualizações para outros clientes interessados'''

    def on_close(self):
        '''Remove registros'''

if __name__ == '__main__':
    try:
        application = Application([
            (r'/(?P<sprint>[0-9]+)', SprintHandler),
        ])
        application.listen(8080)
        IOLoop.instance().start()
    except KeyboardInterrupt as ex:
        print(ex)
