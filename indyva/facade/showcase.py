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

    def get_case(self, name):
        case = self._cases.get(name)
        if case is None:
            case = self._cases[name] = Case()
        return case


class Case(dict):
    def __setitem__(self, *args, **kwargs):
        Showcase.instance().put(args[1])
        return dict.__setitem__(self, *args, **kwargs)
