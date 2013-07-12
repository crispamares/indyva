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
    def wrap(func):
        queue = Loop.get_queue(queue_name)
        @wraps(func)
        def deferred(*args, **kwargs):
            queue.append( (func, args, kwargs) )
        return deferred if DEFERRING else func
    return wrap


when_render = defer('render')


class Loop(object):
    '''
    The event loop sorts and prioritizes the reactions to the events. 
    '''

    _queues = {}
    _render = deque()
    _queues['render'] = _render

    @classmethod
    def get_queue(cls, name):
        return cls._queues[name]
    
    @classmethod
    def exec_queue(cls, queue):
        freezed_render = copy(queue)
        queue.clear()
        while len(freezed_render):
            func, args, kwargs = freezed_render.pop()
            func(*args, **kwargs)
            
    @classmethod
    def run(cls):
        while True:
            
            cls.exec_queue(cls._render)
            
            time.sleep(FREQ)
            

if __name__ == '__main__':
    
    @when_render
    def say_hello(a1, a2):
        print 'hello', a1, a2
        
    
    say_hello(1, a2='ij')
    print 'running...'
    Loop.run()
    
    
    