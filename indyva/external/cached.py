# -*- coding: utf-8 -*-
'''
Created on Oct 10, 2013

@author: crispamares

Based in lazy v1.1 -> https://pypi.python.org/pypi/lazy
'''
import functools

class cached(object):
    """cached is like lazy but return a method not a property

    Used as a decorator to create cached function. Cached functions
    are evaluated on first use.
    """

    def __init__(self, func):
        self.__func = func
        functools.wraps(self.__func)(self)

    def _run(self, inst, inst_cls):
        if inst is None:
            return self

        if not hasattr(inst, '__dict__'):
            raise AttributeError("'%s' object has no attribute '__dict__'" % (inst_cls.__name__,))

        name = self.__name__
        if name.startswith('__') and not name.endswith('__'):
            name = '_%s%s' % (inst_cls.__name__, name)

        cache = inst.__dict__.setdefault('__cache', {})
        if name in cache:
            return cache[name]
        value = self.__func(inst)
        cache[name] = value
        return value

    def __get__(self, inst, inst_cls):
        '''Support instance methods.'''
        return functools.partial(self._run, inst, inst_cls)
       
    @classmethod
    def invalidate(cls, inst, name):
        """Invalidate a lazy attribute.

        This obviously violates the lazy contract. A subclass of lazy
        may however have a contract where invalidation is appropriate.
        """
        inst_cls = inst.__class__

        if not hasattr(inst, '__dict__'):
            raise AttributeError("'%s' object has no attribute '__dict__'" % (inst_cls.__name__,))

        if name.startswith('__') and not name.endswith('__'):
            name = '_%s%s' % (inst_cls.__name__, name)

        cache = inst.__dict__.get('__cache', None)
        if cache and name in cache:
            del cache[name]


