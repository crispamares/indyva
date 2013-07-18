# -*- coding: utf-8 -*-
'''
Created on 11/07/2013

@author: jmorales
'''

import time
from functools import wraps
from collections import deque
from copy import copy

FREQ = 0.001
DEFERRING = True
        
        
def defer(queue_name):
    '''Decorator that defers the execution of the given function. The function
    will be appended to the given queue of the event loop so the moment of the
    execution will depend on the state of those queues'''
    def wrap(func):
        queue = Loop.get_queue(queue_name)
        @wraps(func)
        def deferred(*args, **kwargs):
            queue.append( (func, args, kwargs) )
        return deferred if DEFERRING else func
    return wrap


when_render = defer('render')
when_idle = defer('idle')
when_message = defer('message')


class Loop(object):
    '''
    The event loop sorts and prioritizes the reactions to the events. 
    '''

    _queues = {}
    _render = deque()
    _idle = deque()
    _message = deque()
    _queues['render'] = _render
    _queues['idle'] = _idle
    _queues['message'] = _message

    @classmethod
    def get_queue(cls, name):
        return cls._queues[name]
    
    @classmethod
    def exec_queue(cls, queue):
        freezed_queue = copy(queue)
        queue.clear()
        while len(freezed_queue):
            func, args, kwargs = freezed_queue.pop()
            func(*args, **kwargs)
            
    @classmethod
    def run(cls):
        while True:
            
            cls.exec_queue(cls._message)
            cls.exec_queue(cls._render)
            
            # The idle queue only executes one function per cycle
            if len(cls._idle):
                func, args, kwargs = cls._idle.pop()
                func(*args, **kwargs)
            
            time.sleep(FREQ)
            

if __name__ == '__main__':
    
    @when_render
    def say_hello(a1, a2):
        print 'hello', a1, a2
        
    
    say_hello(1, a2='ij')
    print 'running...'
    Loop.run()
    
    
    