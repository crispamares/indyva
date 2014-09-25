# -*- coding: utf-8 -*-
'''
Created on Oct 17, 2013

@author: crispamares
'''

from zmq.eventloop import IOLoop
from zmq.eventloop.minitornado.ioloop import PeriodicCallback
import uuid

from .loop import Loop


class ZMQLoop(Loop):

    _singleton_cls = Loop

    def __init__(self):
        self.loop = IOLoop.instance()
        self._periodics = {}

    def start(self):
        self.loop.start()

    def stop(self):
        for periodic in self._periodics:
            self.stop_periodic(periodic)
        self.loop.stop()

    def add_periodic_callback(self, callback, interval, name=None, start=False):
        '''
        :param callback callable:
        :param interval float: Interval time in ms
        '''
        name = name if name else uuid.uuid4()
        self.stop_periodic(name)
        periodic = PeriodicCallback(callback, interval, self.loop)
        self._periodics[name] = periodic

        if start:
            self.start_periodic(name)

        return name

    def stop_periodic(self, name):
        periodic = self._periodics.get(name, None)
        if periodic is not None:
            periodic.stop()

    def start_periodic(self, name):
        periodic = self._periodics.get(name, None)
        if periodic is not None and not periodic._running:
            periodic.start()
