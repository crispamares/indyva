# -*- coding: utf-8 -*-
'''
Created on 11/07/2013

@author: jmorales
'''

import time

from indyva.core import Singleton


class Loop(Singleton):
    '''
    An asynchronous scheduler
    '''

    @classmethod
    def clear(cls):
        if hasattr(cls, "_instance"):
            cls._instance.stop()
            del cls._instance

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def add_periodic_callback(self, callback, interval, name, start=False):
        '''
        :param callback callable:
        :param interval float: Interval time in ms
        '''
        raise NotImplementedError()

    def stop_periodic(self, name):
        raise NotImplementedError()

    def start_periodic(self, name):
        raise NotImplementedError()

    def time(self):
        return time.time()



if __name__ == '__main__':
    pass
