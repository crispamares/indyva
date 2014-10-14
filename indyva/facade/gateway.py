'''
Created on Nov 5, 2013

@author: crispamares
'''
import json
import zmq.green as zmq
from geventwebsocket.server import WebSocketServer
from geventwebsocket.resource import WebSocketApplication
import gevent

from indyva.core.names import INamed
from indyva.core.configuration import get_random_port
from indyva.epubsub.bus import Bus
from indyva import for_json_bridge


class Gateway(INamed):
    '''
    Is the facade for the Pub/Sub system to external clients
    Acts as the bridge between the hub and clients in other transports
    '''
    def __init__(self, name, port=None):
        self._bus = Bus(prefix='')
        self.port = port if port is not None else get_random_port()
        INamed.__init__(self, name)

    def publish(self, topic, msg):
        raise NotImplementedError()

    def subscribe(self, topic):
        self._bus.subscribe(topic, self.publish)

    def subscribe_once(self, topic):
        self._bus.subscribe_once(topic, self.publish)

    def unsubscribe(self, topic):
        self._bus.unsubscribe(topic, self.publish)

    def clear(self):
        self._bus.clear()


class ZMQGateway(Gateway):
    def __init__(self, name, port=None):
        Gateway.__init__(self, name, port)

        ctx = zmq.Context.instance()
        self.socket = ctx.socket(zmq.PUB)
        self.socket.bind('tcp://*:' + str(self.port))

    def publish(self, topic, msg):
        msg_json = json.dumps(msg, default=for_json_bridge)
        self.socket.send_multipart([str(topic), msg_json])



class WSGateway(Gateway):

    ws_server = None
    gateways = None

    def __init__(self, name, port=None):
        Gateway.__init__(self, name, port)
        self._sockets = []
        self._msg_queue = []
        if self.ws_server is None:
            self._new_server()

    def _new_server(self):
        cls = self.__class__
        cls.ws_server = WebSocketServer(('',self.port), self.bundler_app)
        gevent.spawn(self.ws_server.serve_forever)

    def publish(self, topic, msg):
        msg_json = json.dumps({'topic':topic,'msg':msg}, default=for_json_bridge)
        if len(self._sockets):
            for ws in self._sockets:
                ws.send(msg_json)
        else:
            self._msg_queue.append(msg_json)

    def _flush(self):
        for msg_json in self._msg_queue:
            for ws in self._sockets:
                ws.send(msg_json)
        self._msg_queue = []

    @classmethod
    def bundler_app(cls, environ, start_response):
        '''
        This WSGI application bundles the gateway specified in the path of
        the url ("/hub/<gateway>") with the WSApplication.

        So at the end, a Gateway will have several WebSockets, one per
        associated WSApplication.
        '''

        if 'wsgi.websocket' not in environ:
            raise Exception("Only WebSocket connections are allowed")

        path = environ["PATH_INFO"]
        if not path.startswith("/hub/"):
            raise Exception("The connection MUST has a path of the from: '/hub/<gateway>'")
        name = [s for s in path.split('/') if s][-1]
        gateway = cls.gateways[name]

        ws = environ['wsgi.websocket']
        current_app = WSApplication(ws)
        current_app._gateway = gateway
        current_app.handle()


class WSApplication(WebSocketApplication):
    '''
    This class populates the gateway with a ws when the connection is done
    '''
    def on_message(self, msg, *args, **kwargs):
        # create new context
        print 'Gateway msg unexpected: ', msg

    def on_open(self):
        print 'on_open'
        self._gateway._sockets.append(self.ws)
        print '\tafter appending the ws:', self._gateway._sockets
        self._gateway._flush()

    def on_close(self, reason):
        print 'on_close', self.ws, '\t-> reason:', reason
        # assert self._gateway._ws is not None
        self._gateway._sockets.remove(self.ws)


