# -*- coding: utf-8 -*-
'''
Created on 11/07/2013

@author: jmorales
'''

import time


class Loop(object):
    '''
    An asynchronous scheduler
    '''

    @staticmethod
    def instance():
        """Returns a global `Loop` instance.

        :warning: Not ThreadSafe.
        """
        if not hasattr(Loop, "_instance"):
            Loop._instance = Loop()
        return Loop._instance

    @staticmethod
    def clear():
        if hasattr(Loop, "_instance"):
            Loop._instance.stop()
            del Loop._instance

    @staticmethod
    def initialized():
        """Returns true if the singleton instance has been created."""
        return hasattr(Loop, "_instance")

    def install(self):
        """Installs this `Loop` object as the singleton instance.

        This is normally not necessary as `instance()` will create
        an `IOLoop` on demand, but you may want to call `install` to use
        a custom subclass of `Loop`.
        """
        assert not Loop.initialized()
        Loop._instance = self

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
