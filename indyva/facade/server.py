'''
Created on Oct 24, 2013

@author: crispamares
'''
import zmq.green as zmq
import gevent.wsgi
import gevent.queue
from geventwebsocket.server import WebSocketServer

from indyva.external.tinyrpc.transports.websocket import WSServerTransport
from indyva.external.tinyrpc.server.gevent import RPCServerGreenlets
from indyva.external.tinyrpc.transports.zmq import ZmqServerTransport
from indyva.external.tinyrpc.transports.wsgi import WsgiServerTransport
from indyva.external.tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from .dispatcher import Dispatcher

import os
import sys
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect


class ZMQServer(RPCServerGreenlets):
    def __init__(self, port=10111):
        ctx = zmq.Context.instance()
        transport = ZmqServerTransport.create(ctx, 'tcp://*:' + str(port))
        protocol = JSONRPCProtocol()
        dispatcher = Dispatcher.instance()
        RPCServerGreenlets.__init__(self, transport, protocol, dispatcher)


class WSGIServer(RPCServerGreenlets):
    def __init__(self, port=8080):
        self.port = port
        self.transport = WsgiServerTransport(queue_class=gevent.queue.Queue)
        protocol = JSONRPCProtocol()
        dispatcher = Dispatcher.instance()
        RPCServerGreenlets.__init__(self, self.transport, protocol, dispatcher)

    def serve_forever(self):
        wsgi_server = gevent.wsgi.WSGIServer(('', self.port),
                                             self.transport.handle)
        gevent.spawn(wsgi_server.serve_forever)
        RPCServerGreenlets.serve_forever(self)


class WSServer(RPCServerGreenlets):
    '''
    A Server for websockets RPCs
    '''
    def __init__(self, port=8080, web_dir=None):
        self.port = port

        if web_dir is None:
            app_root = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
            web_dir = os.path.join(app_root, 'web')
            print '**********', web_dir

        static_app = SharedDataMiddleware(redirect('/s/index.html'), {'/s': web_dir})

        self.transport = WSServerTransport(queue_class=gevent.queue.Queue,
                                           wsgi_handler=static_app)
        protocol = JSONRPCProtocol()
        dispatcher = Dispatcher.instance()
        RPCServerGreenlets.__init__(self, self.transport, protocol, dispatcher)

    def serve_forever(self):
        ws_server = WebSocketServer(('', self.port),
                                    self.transport.handle)
        gevent.spawn(ws_server.serve_forever)
        RPCServerGreenlets.serve_forever(self)
