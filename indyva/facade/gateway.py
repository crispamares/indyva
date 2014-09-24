'''
Created on Nov 5, 2013

@author: crispamares
'''
import json
import zmq.green as zmq
from geventwebsocket.server import WebSocketServer
from geventwebsocket.resource import WebSocketApplication, Resource
import gevent

from indyva.core.names import INamed
from indyva.epubsub.bus import Bus
from indyva import for_json_bridge


class Gateway(INamed):
    '''
    Is the facade for the Pub/Sub system to external clients
    Acts as the bridge between the hub and clients in other transports
    '''
    def __init__(self, name, port):
        self._bus = Bus(prefix='')
        self.port = port
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
    def __init__(self, name, port):
        Gateway.__init__(self, name, port)

        ctx = zmq.Context.instance()
        self.socket = ctx.socket(zmq.PUB)
        self.socket.bind('tcp://*:' + str(port))

    def publish(self, topic, msg):
        print self.name + " ---- publishing --- "
        msg_json = json.dumps(msg, default=for_json_bridge)
        self.socket.send_multipart([str(topic), msg_json])



class WSGateway(Gateway):

    def __init__(self, name, port):
        Gateway.__init__(self, name, port)
        self._sockets = []
        self._msg_queue = []
        self.ws_server = WebSocketServer(('', port),
                                         Resource({'/ws': WSApplicationFactory(self)}))
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


class WSApplicationFactory(object):
    '''
    Creates WebSocketApplications that can communicates with the gateway.
    '''
    def __init__(self, gateway):
        self._gateway = gateway

    def __call__(self, ws):
        '''
        The fake __init__ for the WSApplication
        '''
        app = WSApplication(ws)
        app._gateway = self._gateway
        return app

    @classmethod
    def protocol(cls):
        return WebSocketApplication.protocol()
