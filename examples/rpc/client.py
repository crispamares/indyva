# -*- coding: utf-8 -*-
'''
Created on 18/07/2013

@author: jmorales
'''

import zmq
import json
import timeit

def call_echo(socket, m):
    content = {'service': 'echoer', 'rpc': 'echo', 'args':{'a': m}}
    msg = {'content': content}
    json_msg = json.dumps(msg)
    #print 'sent:', json_msg
    socket.send(json_msg)
    response = socket.recv()
    #print 'response:', response
    
def main():
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect('tcp://127.0.0.1:10111')
    #socket.connect('ipc:///tmp/1')
    
    t0 = timeit.time.time()
    for i in range(10000):
        call_echo(socket, 'hello')
        
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
socket.connect('tcp://127.0.0.1:10111')'''

    print(timeit.repeat("call_echo(socket, 'hello')", setup=setup, number=10000))

def compute_overhead():
    pass

if __name__ == '__main__':
    #main()
    get_times()