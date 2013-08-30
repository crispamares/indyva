# -*- coding: utf-8 -*-
'''
Created on 18/07/2013

@author: jmorales
'''

import loop
from facade import endpoint, front
from dataset import table_service

import zmq

from external.tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from external.tinyrpc.transports.zmq import ZmqServerTransport
from external.tinyrpc.server import RPCServer
from external.tinyrpc.dispatch import RPCDispatcher


ENDPOINTDIR = 'tcp://127.0.0.1:10111'

def main():
    
    ctx = zmq.Context()
    dispatcher = RPCDispatcher()
    table_srv_dispatcher = RPCDispatcher()
    transport = ZmqServerTransport.create(ctx, ENDPOINTDIR)
    
    rpc_server = RPCServer(
                           transport,
                           JSONRPCProtocol(),
                           dispatcher
                           )
    
    service = table_service.TableService('TableSrv')
    service.register_in(table_srv_dispatcher)
    dispatcher.add_subdispatch(table_srv_dispatcher, service.name+'.')
    
    @dispatcher.public
    def echo(s):
        return s

    print 'running'    
    rpc_server.serve_forever()
    print 'stop'
    
if __name__ == '__main__':
    main()