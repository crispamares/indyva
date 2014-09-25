# -*- coding: utf-8 -*-
'''
Created on 16/10/2013

@author: jmorales
'''

from functools import partial
import uuid
import types

import gevent
from gevent.queue import Queue

from indyva.epubsub.hub import Hub


# Total 100 ms to be interactive
# http://www.nngroup.com/articles/response-times-3-important-limits/
FPS = 30
RENDERINTERVAL = 1.0 / FPS  # In seconds
LOOPINTERVAL = 0.00001      # In seconds

PREFIX = dict(control='ctr:', render='r:')


class KernelHub(Hub):
    '''A specialization of :class:`~indyva.epubsub.hub.Hub` that instead of executing the
    callbacks as they arrive, this class defers the callbacks pushing
    them in the different :class:`Kernel` queues.

    The API is exactly the same of :class:`~indyva.epubsub.hub.Hub`

    '''

    _singleton_cls = Hub

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
    '''The kernel has executive responsibilities. Deals with the
    asynchronous computation of events.

    The kernel encapsulate the main loop of a indyva's application.
    It also groups and makes accessible the hub, the dispatcher
    and the RPC servers.

    When :func:`start` or :func:`run_forever` are called the kernel
    spawns all the servers and two more concurrent processes. One
    process runs the main loop, calling :func:`do_one_iteration` until
    the execution is stopped. And the other process generate a render
    message with topic 'r:' every render_interval. Any view can
    subscribe to this topic and check if it needs a refresh. With this
    mechanism you can easily synchronize independent views because
    messages arrive in the same order so all the views will render the
    same state.

    The kernel controls the execution of asynchronous reactions with a
    set queues with different priorities.

    Control queue:
      All control events are processed per loop.

    Message queue:
      One message event is processed per loop.

      This is the queue where PUB/SUB messages are placed in.

    Render queue:
      All render events are processed per loop but
      typically the max length is 1.

    Idle queue:
      One idle event is processed per loop but only if the message
      queue is empty.

      Use this queue for 'background' low priority tasks.

    Instead of the plain :class:`~indyva.epubsub.hub.Hub` the kernel uses a
    instance of a KernelHub, so every event message is queued into the
    kernel's queues and processed later. Basically, the execution of
    the callback is deferred (:func:`defer`) on time so the kernel
    can reorder and give priorities to each message.

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
        '''Start the event loop and all the servers added before calling this
        method.  Returns a list of Greenlets so you can do a joinall
        if you want to block.

        :returns: [Greenlets]

        '''
        greenlets = []
        for server in self._servers:
            greenlets.append(server.start())
        # WARNING: qtgevent has a bug and if the _init_loop is run before servers
        #     those servers never run
        greenlets.append(gevent.spawn(self._init_loop))
        greenlets.append(gevent.spawn(self._init_render))

        return greenlets

    def run_forever(self):
        '''
        Start the event loop and all the servers added before calling this
        method. This is a blocking method.

        '''
        gevent.joinall(self.start())

    def _init_loop(self):
        while True:
            if self.are_queues_empty():
                self._new_message.clear()
                self._new_message.wait()
            self.do_one_iteration()

    def _init_render(self):
        def publish_render():
            self.hub.publish(PREFIX['render'], {'id': str(uuid.uuid4())})
        defer_publish = partial(self.defer, self._render, publish_render)
        while True:
            gevent.sleep(self._render_interval)
            defer_publish()  # render queue blocks... maxsize == 1

    def add_server(self, server):
        '''This method should be called before starting the kernel.

        :param facade.server.RPCServer server: Server to add
        '''
        self._servers.append(server)

    def are_queues_empty(self):
        '''
        :returns: Bool
        '''
        return all([q.empty() for q in self._queues.values()])

    def defer(self, queue, func, *args, **kwargs):
        '''
        Defers the execution of the function.

        :param str queue: The queue where the execution will be
        queued. A :class:`gevent.queue.Queue` is also valid.
        :param callable func: Any callable to be deferred
        :param list args: The list of arguments to pass to the deferred func
        :param dict kwargs: A dict of arguments to pass to the deferred func
        '''
        if isinstance(queue, types.StringTypes):
            queue = self._queues[queue]
        queue.put( (func, args, kwargs) )
        self._new_message.set()

    def flush(self, queue, num=0):
        '''
        Process a number of messages of the specified Queue.

        :param gevent.queue.Queue queue: The queue to flush
        :param int num: The max number of message to process. 0 means process all
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
        '''In this order: process all control msgs, process one message,
        process all render msgs, and if message queue is empty then
        process one idle msg

        '''
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
