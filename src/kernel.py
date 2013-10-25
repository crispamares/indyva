# -*- coding: utf-8 -*-
'''
Created on 16/10/2013

@author: jmorales
'''

from collections import deque
from epubsub.hub import Hub, PREFIX
from functools import partial
import uuid


from eventloop import Loop
import types

# Total 100 ms to be interactive
# http://www.nngroup.com/articles/response-times-3-important-limits/
FPS = 30
RENDERINTERVAL = 1000 / FPS
POLLINTERVAL = 10 
LOOPINTERVAL = 0.01


class KernelHub(Hub):
    
    def __init__(self, kernel):
        self._kernel = kernel
        Hub.__init__(self)

    def _send_msg(self, destination, topic, msg):
        '''
        :param str topic: 
        '''
        if topic.startswith(PREFIX['render']):
            destination(topic, msg)
            return

        if topic.startswith(PREFIX['control']):
            queue = 'control'
        else:
            queue = 'message'
        self._kernel.defer(queue, destination, topic, msg)
        

class Kernel(object):
    '''
    The kernel has executive responsibilities. Deals with the asynchronous 
    computation of events 
    '''
    
    def __init__(self, loop=None, loop_interval=LOOPINTERVAL, 
                              render_interval=RENDERINTERVAL,
                              poll_interval=POLLINTERVAL):
        '''
        :param Loop loop: 
        '''
        self._loop = loop if loop else Loop.instance()
        self.hub = KernelHub(self)
        self.hub.install()
        
        self._render_interval = render_interval
        self._loop_interval = loop_interval
        self._poll_interval = poll_interval
        
        self._servers = []
        
        self._queues = {}
        self._render = deque(maxlen=1)
        self._idle = deque()
        self._message = deque()
        self._control = deque()
        self._queues['control'] = self._control
        self._queues['message'] = self._message
        self._queues['render'] = self._render
        self._queues['idle'] = self._idle

        self.loop_periodic = None
        self._init_loop()
        self._init_reder()


    def _init_loop(self):
        self.loop_periodic = self._loop.add_periodic_callback(
            self.do_one_iteration, self._loop_interval, start=True)
    
    def _init_reder(self):
        def publish_render():
            Hub.instance().publish(PREFIX['render'], {id : uuid.uuid4()})
        defer_publish = partial(self.defer, self._render, publish_render)
        self._loop.add_periodic_callback(defer_publish, 
            self._render_interval, start=True)

    def _init_poll(self):
        def publish_poll():
            Hub.instance().publish(PREFIX['control']+'poll', {id : uuid.uuid4()})
        defer_publish = partial(self.defer, self._control, publish_poll)
        self._loop.add_periodic_callback(defer_publish, 
            self._poll_interval, start=True)
    
    def add_server(self, server):
        self._servers.append(server)
        self.hub.subscribe(PREFIX['control']+'poll', server.poll)
        self._init_poll()
        
    
    def defer(self, queue, func, *args, **kwargs):
        self._loop.start_periodic(self.loop_periodic)
        if isinstance(queue, types.StringTypes):
            queue = self._queues[queue]
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
        if (not self._control and not self._message and not self._idle):
            self._loop.stop_periodic(self.loop_periodic)
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



#DEFERRING = True
#def defer(queue_name):
#    '''Decorator that defers the execution of the given function. The function
#    will be appended to the given queue of the event loop so the moment of the
#    execution will depend on the state of those queues'''
#    def wrap(func):
#        queue = Loop.get_queue(queue_name)
#        @wraps(func)
#        def deferred(*args, **kwargs):
#            queue.append( (func, args, kwargs) )
#        return deferred if DEFERRING else func
#    return wrap
#
#
#when_render = defer('render')
#when_idle = defer('idle')
#when_message = defer('message')


if __name__ == '__main__':
    pass