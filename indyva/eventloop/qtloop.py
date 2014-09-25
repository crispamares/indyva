# -*- coding: utf-8 -*-
'''
Created on Oct 17, 2013

@author: crispamares
'''

from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QTimer
import uuid

from .loop import Loop


class QtLoop(Loop):

    _singleton_cls = Loop

    def __init__(self):
        self.loop = QApplication.instance()
        if self.loop is None:
            raise AssertionError(
                'QApplication must be initialized before creating QtLoop object')
        self._periodics = {}

    def start(self):
        self.loop.exec_()

    def stop(self):
        for periodic in self._periodics:
            self.stop_periodic(periodic)
        self.loop.quit()

    def add_periodic_callback(self, callback, interval, name=None, start=False):
        '''
        :param callback callable:
        :param interval float: Interval time in ms
        '''
        name = name if name else uuid.uuid4()
        self.stop_periodic(name)

        timer = QTimer()
        timer.timeout.connect(callback)
        timer.setInterval(interval)

        self._periodics[name] = timer

        if start:
            self.start_periodic(name)

        return name

    def stop_periodic(self, name):
        periodic = self._periodics.get(name, None)
        if periodic is not None:
            periodic.stop()

    def start_periodic(self, name):
        periodic = self._periodics.get(name, None)
        if periodic is not None and not periodic.isActive():
            periodic.start()
