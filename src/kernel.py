# -*- coding: utf-8 -*-
'''
Created on 16/10/2013

@author: jmorales
'''

from collections import deque
from epubsub import hub
from functools import partial
import uuid

FPS = 30
RENDERINTERVAL = 1000 / FPS 
LOOPINTERVAL = 0.01

class Kernel(object):
    '''
    The kernel has executive responsibilities. Deals with the asynchronous 
    computation of events 
    '''
    
    def __init__(self, loop, loop_interval=LOOPINTERVAL, 
                              render_interval=RENDERINTERVAL):
        self._loop = loop
        
        self._render_interval = render_interval
        self._loop_interval = loop_interval
        
        self._queues = {}
        self._render = deque(maxlen=1)
        self._idle = deque()
        self._message = deque()
        self._control = deque()
        self._queues['control'] = self._control
        self._queues['message'] = self._message
        self._queues['render'] = self._render
        self._queues['idle'] = self._idle

        self._init_reder()

    def _get_queue(self, name):
        return self._queues[name]
    
    def _init_reder(self):
        def publish_render():
            hub.instance().publish('r.', {id : uuid.uuid4()})
        defer_publish = partial(self.defer, self._render, publish_render)
        self._loop.add_periodic_callback(defer_publish, self._render_interval)
    
    def defer(self, queue, func, args=None, kwargs=None):
        queue.appendleft( (func, args, kwargs) )
        
    def flush(self, queue, num=0):
        '''
        :param collections.deque queue
        '''
        num = min(num, len(queue))
        i = 0
        while queue:
            if num and i >= num: break
            func, args, kwargs = queue.pop()
            func(*args, **kwargs)
            i += 1
        return i
            
    def do_one_iteration(self):
        # process all control msgs
        self.flush(self._control)
        # process one msg
        self.flush(self._message, 1)
        # recv and send in sockets
        #######################################################
        # process render msgs 
        self.flush(self._render)
        # if msgs.empty: process one idle
        if not self._message:
            self.flush(self._idle, 1)

if __name__ == '__main__':
    pass