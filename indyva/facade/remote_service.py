# -*- coding: utf-8 -*-
'''
Created on 09/12/2013

@author: jmorales
'''


from functools import partial
import zmq.green as zmq

from indyva.external.tinyrpc.transports.zmq import ZmqClientTransport
from indyva.external.tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from indyva.external.tinyrpc.client import RPCClient
from indyva.core.names import INamed


class RemoteService(INamed):

    def __init__(self, endpoint, srv_description, name):
        '''
        :param str endpoint: The ZeroMQ endpoint definition
        :param dict srv_description: The description of the exposed methods
            * Has the form:
                {method_name: {params: ['name_param', 'data type, description, default=val (if optional)'],
                               return: 'description with data type, maybe using the same structure (like list or dict)'}}
            * Currently is used mainly for online documentation proposes, only
            the method_name has effect on the code behavior
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
