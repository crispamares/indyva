'''
Created on Oct 24, 2013

@author: crispamares
'''

from external.tinyrpc.transports.zmq import ZmqServerTransport
from external.tinyrpc.transports.wsgi import WsgiServerTransport
import zmq.green as zmq 
from external.tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from facade import Front
from external.tinyrpc.server.gevent import RPCServerGreenlets

import gevent
import gevent.wsgi
import gevent.queue
from external.tinyrpc.transports.websocket import WSServerTransport
from geventwebsocket.server import WebSocketServer

class ZMQServer(RPCServerGreenlets):
    def __init__(self, port=10111):
        ctx = zmq.Context()
        transport = ZmqServerTransport.create(ctx, 'tcp://127.0.0.1:'+str(port))
        protocol = JSONRPCProtocol()
        dispatcher = Front()
        RPCServerGreenlets.__init__(self, transport, protocol, dispatcher)

class WSGIServer(RPCServerGreenlets):
    def __init__(self, port=8080):
        self.port = port
        self.transport = WsgiServerTransport(queue_class=gevent.queue.Queue)
        protocol = JSONRPCProtocol()
        dispatcher = Front()
        RPCServerGreenlets.__init__(self, self.transport, protocol, dispatcher)
        
    def serve_forever(self):
        wsgi_server = gevent.wsgi.WSGIServer(('127.0.0.1', self.port), 
            self.transport.handle)
        gevent.spawn(wsgi_server.serve_forever)
        RPCServerGreenlets.serve_forever(self)

class WSServer(RPCServerGreenlets):
    '''
    A Server for websockets RPCs
    '''
    def __init__(self, port=8080):
        self.port = port
        self.transport = WSServerTransport(queue_class=gevent.queue.Queue)
        protocol = JSONRPCProtocol()
        dispatcher = Front()
        RPCServerGreenlets.__init__(self, self.transport, protocol, dispatcher)
        
    def serve_forever(self):
        ws_server = WebSocketServer(('127.0.0.1', self.port), 
            self.transport.handle)
        gevent.spawn(ws_server.serve_forever)
        RPCServerGreenlets.serve_forever(self)    