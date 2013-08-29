# -*- coding: utf-8 -*-
'''
Created on 18/07/2013

@author: jmorales
'''

import zmq
import json
import timeit

def call_echo(socket, m):
    content = {'service': '_builtin', 'rpc': 'echo', 'args': [m]}
    msg = {'content': content}
    json_msg = json.dumps(msg)
    #print 'sent:', json_msg
    socket.send(json_msg)
    response = socket.recv()
    #print 'response:', response

def call(socket, content):
    msg = {'content': content}
    json_msg = json.dumps(msg)
    socket.send(json_msg)
    return socket.recv()
    
def main():
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect('tcp://127.0.0.1:10111')

    from dataset import RSC_DIR
    import pandas as pn 

    df = pn.read_csv(RSC_DIR+'/census.csv')
    data = []
    for i in range(len(df)):
        data.append(df.ix[i].to_dict())
    with open(RSC_DIR+'/schema_census') as f:
        schema = json.loads(f.read())
    schema = dict(attributes = schema['attributes'], index = schema['index'])
    
    t0 = timeit.time.time()
    #for i in range(100):
        #call_echo(socket, 'hello')
    call(socket, {'service': 'TableSrv', 'rpc': 'new_table', 'args': ['table1', schema, data]})
    print call(socket, {'service': 'table1', 'rpc': 'find', 'args': [{}]})
    call(socket, {'service': 'TableSrv', 'rpc': 'del_table', 'args': ['table1']})
    t1 = timeit.time.time()
    print 'time: ', t1 - t0
    
def get_times():
    print 'measuring time...'
    setup = '''
import zmq
import json
from __main__ import call_echo
ctx = zmq.Context()
socket = ctx.socket(zmq.REQ)
socket.connect('tcp://127.0.0.1:10111')
m = 'hello'*1000
'''
    n = 10000

    r = timeit.repeat("call_echo(socket, m)", setup=setup, number=n)
    print 'time per msg:', [ t/n for t in r]
    print 'total time (%d) messages:'%n, r
    print 'messages per second:', [ n/t for t in r]

def compute_overhead():
    pass

if __name__ == '__main__':
    main()
    #get_times()