# -*- coding: utf-8 -*-
'''
Created on 23/10/2013

@author: jmorales
'''
from uuid import uuid4
from indyva.core.context import SessionSingleton


class ExistingNameError(ValueError):
    pass


class INamed(object):
    '''
    Objects that inherit this Class will be created with a trusted unique name

    Actually, what is unique, is the oid. It is registered in the
    NameAuthority.
    '''
    def __init__(self, name, prefix=''):
        authority = NameAuthority.instance()
        prefix = str(prefix)
        if name is None:
            name = authority.new_name()
        self._name = name
        self._prefix = prefix

        self._initializing = True
        authority.register(self.oid)
        self._initializing = False

    @property
    def name(self):
        return self._name

    @property
    def oid(self):
        '''An oid (object id) is a unique identificator based on the name'''
        return self._prefix + self._name

    def __del__(self):
        if not self._initializing:
            authority = NameAuthority.instance()
            authority.unresgister(self._prefix + self._name)

    def for_json(self):
        return self.oid


class NameAuthority(SessionSingleton):
    '''
    This class creates or ensures unique names in the name space
    '''

    def __init__(self):
        self._names = {}

    def register(self, name):
        '''
        Register a name. This method raises an ExistingNameError if the
        name is already registered
        '''
        print 'registering', name
        if name in self._names:
            raise ExistingNameError('"{0}" already registered'.format(name))
        else:
            self._names[name] = None

    def unresgister(self, name):
        '''
        Unregister the name so the same name can be registered in the
        future
        '''
        print 'unregistering', name
        self._names.pop(name, None)

    def new_name(self):
        '''
        Creates a random uuid

        :return str name
        '''
        name = str(uuid4())
        return name

    def clear(self):
        self._names.clear()


def register(name):
    authority = NameAuthority.instance()
    return authority.register(name)


def unregister(name):
    authority = NameAuthority.instance()
    return authority.unregister(name)


def new_name():
    authority = NameAuthority.instance()
    return authority.new_name()


def clear():
    authority = NameAuthority.instance()
    return authority.clear()
