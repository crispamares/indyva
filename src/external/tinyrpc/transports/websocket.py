#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Queue

from . import ServerTransport
from geventwebsocket.resource import WebSocketApplication, Resource


class WSApplicationFactory(object):
    '''
    Creates WebSocketApplications with a messages queue and the queue_class 
    needed for the communication with the transport 
    '''
    def __init__(self, messages, queue_class):
        self.messages = messages
        self._queue_class = queue_class
        
    def __call__(self, ws):
        '''
        The fake __init__ for the WSApplication
        '''
        app = WSApplication(ws)
        app.messages = self.messages
        app._queue_class = self._queue_class
        return app 
    
    @classmethod
    def protocol(cls):
        return WebSocketApplication.protocol()

class WSApplication(WebSocketApplication):

    def on_message(self, msg, *args, **kwargs):
        # create new context
        context = self._queue_class()
        self.messages.put((context, msg))
        response = context.get()
        self.ws.send(response, *args, **kwargs)

class WSServerTransport(ServerTransport):
    def __init__(self, queue_class=Queue.Queue, wsgi_handler=None):
        self._queue_class = queue_class
        self.messages = queue_class()
    
        def static_wsgi_app(environ, start_response):
            start_response("200 OK", [("Content-Type", "text/html")])
            return 'Ready for WebSocket connection in /ws'

        self.handle = Resource(
            {'/': static_wsgi_app if wsgi_handler is None else wsgi_handler,
             '/ws': WSApplicationFactory(self.messages, queue_class)})

    def receive_message(self):
        return self.messages.get()

    def send_reply(self, context, reply):
        context.put(reply)
