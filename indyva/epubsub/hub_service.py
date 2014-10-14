'''
Created on Nov 5, 2013

@author: crispamares
'''
from indyva.core.names import INamed
from indyva.facade.gateway import WSGateway, ZMQGateway
from .hub import Hub


class HubService(INamed):
    '''
    This class provide a facade for the pub/sub mechanism. This class also
    allows remote clients to create gateways so the connection can be done
    between different transports.
    '''

    def __init__(self, name='HubSrv'):
        '''
        :param name: The unique name of the service
        '''
        self._gateways = {}
        self.hub = None
        WSGateway.gateways = self._gateways

        INamed.__init__(self, name)

    def register_in(self, dispatcher):
        dispatcher.add_method(self.publish)
        dispatcher.add_method(self.subscribe)
        dispatcher.add_method(self.subscribe_once)
        dispatcher.add_method(self.unsubscribe)
        dispatcher.add_method(self.clear)
        dispatcher.add_method(self.new_gateway)
        dispatcher.add_method(self.del_gateway)

    def publish(self, topic, msg):
        self.hub = self.hub if self.hub is not None else Hub.instance()
        self.hub.publish(topic, msg)

    def subscribe(self, gateway, topic):
        gw = self._gateways[gateway]
        gw.subscribe(topic)

    def subscribe_once(self, gateway, topic):
        gw = self._gateways[gateway]
        gw.subscribe_once(topic)

    def unsubscribe(self, gateway, topic):
        gw = self._gateways[gateway]
        gw.unsubscribe(topic)

    def clear(self, gateway):
        gw = self._gateways[gateway]
        gw.clear()

    def new_gateway(self, name, transport, port=None):
        '''
        If the gateway already exists nothing is done.

        :param str name: The unique name of the gateway
        :param str transport: ['zmq' | 'ws'] The kind of transport to use
        :param int port: The port where clients want to connect, if no provided
        a random por is generated
        :returns int: The port to be use by the gateway
        '''
        if name not in self._gateways:
            if transport == 'zmq':
                self._gateways[name] = ZMQGateway(name, port)
            elif transport == 'ws':
                self._gateways[name] = WSGateway(name, port)
            else:
                raise ValueError('{0} Transport not identified. Supported: "zmq", "ws"'
                                 .format(transport))
        return self._gateways[name].port

    def del_gateway(self, name):
        self._gateways.pop(name)
