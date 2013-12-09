# -*- coding: utf-8 -*-
'''
Created on 09/12/2013

@author: jmorales
'''


from functools import partial
import zmq.green as zmq 

from external.tinyrpc.transports.zmq import ZmqClientTransport
from external.tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from external.tinyrpc.client import RPCClient

from names import INamed

    
class RemoteService(INamed):

    def __init__(self, endpoint, srv_description, name):
        '''
        :param str endpoint: The ZeroMQ endpoint definition
        :param str name: The unique name of the service
        '''
        self.ctx = zmq.Context.instance()
        
        transport = ZmqClientTransport.create(self.ctx, endpoint)
        self.rpc = RPCClient(JSONRPCProtocol(), transport)

        self.endpoint = endpoint
        self.srv_description = srv_description
        INamed.__init__(self, name)

    def register_in(self, dispatcher):
        for rpc_name in self.srv_description:
            dispatcher.add_method(partial(self.proxy_call, rpc_name), rpc_name)
        
    def proxy_call(self, rpc_name, *args, **kwargs):
        return self.rpc.call(rpc_name, args, kwargs)
        
    