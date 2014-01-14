# -*- coding: utf-8 -*-
'''
Created on 18/07/2013

@author: jmorales
'''

import zmq
import json
import timeit

from indyva.external.tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from indyva.external.tinyrpc.transports.zmq import ZmqClientTransport
from indyva.external.tinyrpc import RPCClient, RPCProxy
#from indyva.external.tinyrpc.transports.http import HttpPostClientTransport


def raw_call(socket, method, params):
    ''' This is the call that other languages has to implement '''
           
    msg = {'jsonrpc': JSONRPCProtocol.JSON_RPC_VERSION,
           'id': 1,  # This should not be a constant, but a unique id
           'method': method,
           'params':params
       }
    json_msg = json.dumps(msg)
    socket.send(json_msg)
    return socket.recv()


    
def main():
    use_zmq = True
    use_http = not use_zmq
    
    
    if use_zmq:
        ctx = zmq.Context()
        transport = ZmqClientTransport.create(ctx, 'tcp://127.0.0.1:10111')
        rpc_client = RPCClient(JSONRPCProtocol(), transport)
    elif use_http:
        rpc_client = RPCClient(
            JSONRPCProtocol(),
            HttpPostClientTransport('http://127.0.0.1:8080/')
            )


    if use_zmq:
        res = raw_call(transport.socket, 'echo', {'s':'Ping'})
        print 'Raw call result:', res
        res = raw_call(transport.socket, 'echo', ['Pong'])
        print 'Raw call result:', res
    
    remote_server = rpc_client.get_proxy()
    schema, data = _get_data()
    
    result = rpc_client.call('TableSrv.new_table', args=['table1', data, schema], kwargs=None)
    print 'Client result:', result
    
    #table_service = RPCProxy(rpc_client, prefix='TableSrv.')
    table_service = rpc_client.get_proxy(prefix='TableSrv.')
    table2 = table_service.new_table('table2', data, schema)
    print 'Proxy result:', result
    
    result = table_service.find(table2, {'$or':[{'State': 'NY'},{'State': 'DC'}]})
    print 'Proxy result:', result
    
    result = table_service.insert(table2, {'State': 'MD', 'LiveMeanning': 42})
    print 'Proxy result:', result
    
    result = table_service.get_data(table2)
    print 'Proxy result:', result
    
    result = remote_server.echo('Hello, World!')
    print "Server answered:", result
        
    #remote_server.tables_container.new_table()
    
    dselect = rpc_client.call('DynSelectSrv.new_dselect', args=['dselect', table2], kwargs=None)
    print 'New dselect', dselect

    result = rpc_client.call('DynSelectSrv.new_categorical_condition', [dselect, 'State',[],'cond1'], kwargs=None)
    print 'New Categorical Condition', result
    
    # ==========================================================================
    #      Batch request is implemented in tinyrpc but not the response.
    # =========================================================================
    #result = rpc_client.batch_call([['echo', ['Hello 1']], ['echo', ['Hello 2']]])
    #print 'Batch result:', result
                                    

def _get_data():
    from indyva.dataset import RSC_DIR
    import pandas as pn 

    df = pn.read_csv(RSC_DIR+'/census.csv')
    data = []
    for i in range(len(df)):
        data.append(df.ix[i].to_dict())
    with open(RSC_DIR+'/schema_census') as f:
        schema = json.loads(f.read())
    schema = dict(attributes = schema['attributes'], index = schema['index'])
    return schema, data

    
def get_times():
    print 'measuring time...'
    setup = '''
from indyva.external.tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from indyva.external.tinyrpc.transports.zmq import ZmqClientTransport
from indyva.external.tinyrpc import RPCClient

import zmq
import json
from __main__ import raw_call

ctx = zmq.Context()
transport = ZmqClientTransport.create(ctx, 'tcp://127.0.0.1:10111')
rpc_client = RPCClient(JSONRPCProtocol(), transport)

m = 'hello'*1
'''
    n = 1000

    r = timeit.repeat("raw_call(transport.socket, 'echo', [m])", setup=setup, number=n)
    print 'time per msg:', [ t/n for t in r]
    print 'total time (%d) messages:'%n, r
    print 'messages per second:', [ n/t for t in r]

def compute_overhead():
    pass

if __name__ == '__main__':
    main()
    #get_times()