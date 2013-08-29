# -*- coding: utf-8 -*-
'''
Created on 17/07/2013

@author: jmorales
'''
import zmq
import front
from loop import when_message
import json


ENDPOINTDIR = 'tcp://127.0.0.1:10111'


def json_magic(o):
    try:
        return o.for_json()
    except AttributeError, e:
        print e
        raise TypeError('{0} is not JSON serializable'.format(o))

class Endpoint(object):
    '''
    This class exposes the Front to remote clients over ZeroMQ transport layer
    
    It is also integrated with the event loop
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.front = front.get_instance()
        self.ctx = zmq.Context()
        
        self.socket = self.ctx.socket(zmq.REP)
        self.socket.bind(ENDPOINTDIR)
        self._stopped = True
        self._interrupted = False

    @when_message
    def recive(self):
        try:
            event = self.socket.poll(1)
            if event:
                json_msg = self.socket.recv()
                msg = json.loads(json_msg)
                response = self.front.call(msg['content'])
                json_response = json.dumps(response, default=json_magic)
                self.socket.send(json_response)
        except zmq.ZMQError:  #eg: SIGINT
            pass
        if not self._stopped:
            self.recive()
            
    def fast_recive(self):
        while True:
            json_msg = self.socket.recv()
            msg = json.loads(json_msg)
            response = self.front.call(msg['content'])
            json_response = json.dumps(response, default=json_magic)
            self.socket.send(json_response)
            if self._stopped:
                break
            
    def run(self):  
        self._stopped = False
        self.recive()
    
    def stop(self):
        self._stopped = True
        