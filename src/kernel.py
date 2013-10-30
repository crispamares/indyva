# -*- coding: utf-8 -*-
'''
Created on 16/10/2013

@author: jmorales
'''

from epubsub.hub import Hub, PREFIX
from functools import partial
import uuid

import types
import gevent
from gevent.queue import Queue

# Total 100 ms to be interactive
# http://www.nngroup.com/articles/response-times-3-important-limits/
FPS = 30
RENDERINTERVAL = 1.0 / FPS  # In seconds
LOOPINTERVAL = 0.00001      # In seconds


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
    
    def __init__(self, loop_interval=LOOPINTERVAL,
                        render_interval=RENDERINTERVAL):
        '''
        :param float loop_interval: times in seconds 
        :param float render_interval: times in seconds 
        '''
        self.hub = KernelHub(self)
        self.hub.install()
        
        self._new_message = gevent.event.Event()
        
        self._render_interval = render_interval
        self._loop_interval = loop_interval

        self._servers = []
        
        self._queues = {}
        self._render = Queue(maxsize=1)
        self._idle = Queue()
        self._message = Queue()
        self._control = Queue()
        self._queues['control'] = self._control
        self._queues['message'] = self._message
        self._queues['render'] = self._render
        self._queues['idle'] = self._idle

    def start(self):
        '''
        Start the event loop and all the servers added before calling this 
        method. 
        Returns a list of Greenlets so you can do a joinall if you want to block  
        :return: [Greenlets]
        '''
        greenlets = []
        greenlets.append(gevent.spawn(self._init_loop))
        greenlets.append(gevent.spawn(self._init_render))
        for server in self._servers:
            greenlets.append(gevent.spawn(server.serve_forever))
        return greenlets
    
    def run_forever(self):
        '''
        Start the event loop and all the servers added before calling this 
        method. This is a blocking method.
        '''
        gevent.joinall(self.start())

    def _init_loop(self):
        while True:
            if self.all_empty():
                self._new_message.clear()
                self._new_message.wait()
            self.do_one_iteration()
    
    def _init_render(self):
        def publish_render():
            Hub.instance().publish(PREFIX['render'], {id : uuid.uuid4()})
        defer_publish = partial(self.defer, self._render, publish_render)
        while True:
            gevent.sleep(self._render_interval)
            defer_publish() # render queue blocks... maxsize == 1 
            
    def add_server(self, server):
        self._servers.append(server)
        
    def all_empty(self):
        return all([q.empty() for q in self._queues.values()])
    
    def defer(self, queue, func, *args, **kwargs):
        if isinstance(queue, types.StringTypes):
            queue = self._queues[queue]
        queue.put( (func, args, kwargs) )
        self._new_message.set()
        
    def flush(self, queue, num=0):
        '''
        :param gevent.queue.Queue :
        '''
        num = min(num, queue.qsize())
        i = 0
        while queue.qsize():
            if num and i >= num: break
            func, args, kwargs = queue.get_nowait()
            func(*args, **kwargs)
            i += 1
        return i
            
    def do_one_iteration(self):
        # process all control msgs
        self.flush(self._control)
        # process one msg
        self.flush(self._message, 1)
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