# -*- coding: utf-8 -*-
'''
Created on 20/11/2013

:author: jmorales
'''

from weakref import WeakValueDictionary
from indyva.core.context import SessionSingleton


class Showcase(SessionSingleton):
    '''
    This class enables other classes to translate names previously registered
    to actual objects

    '''

    def __init__(self):
        self._objects = WeakValueDictionary()
        self._cases = WeakValueDictionary()

    def get(self, oid):
        '''
        :param str oid: the oid registered in the NameAuthority
        '''
        return self._objects.get(oid)

    def put(self, instance):
        '''
        :param INamed oid: the exposed object.
        '''
        self._objects[instance.oid] = instance

    def get_case(self, tag, default=None):
        '''
        :param str tag: The tag that the returned case should have
        '''
        return self._cases.get(tag, default)


class Case(dict):
    def __setitem__(self, *args, **kwargs):
        Showcase.instance().put(args[1])
        return dict.__setitem__(self, *args, **kwargs)

    def tag(self, tag):
        Showcase.instance()._cases[tag] = self
        return self
