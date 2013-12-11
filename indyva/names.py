# -*- coding: utf-8 -*-
'''
Created on 23/10/2013

@author: jmorales
'''
from uuid import uuid4


class ExistingNameError(ValueError):
    pass


class INamed(object):
    '''
    Objects that inherit this Class will be created with a trusted unique name  
    '''
    def __init__(self, name, prefix=''):
        authority = NameAuthority.instance()
        prefix = str(prefix)
        if name is None:
            name = authority.new_name(prefix)
        else:
            authority.register(prefix+name)
        self._name = name
        self._prefix = prefix
        
    @property
    def name(self):
        return self._name

    @property
    def full_name(self):
        return self._prefix + self._name
    
    def __del__(self):
        authority = NameAuthority.instance()
        authority.unresgister(self._prefix+self._name)
    
    def for_json(self):
        return self.full_name

class NameAuthority(object):
    '''
    This class creates or ensures unique names in the space name space  
    '''

    def __init__(self):
        self._names = {}
    
    @staticmethod
    def instance():
        """Returns a global `NameAuthority` instance. 
        
        :warning: Not ThreadSafe.
        """
        if not hasattr(NameAuthority, "_instance"):        
            NameAuthority._instance = NameAuthority()
        return NameAuthority._instance

    @staticmethod
    def initialized():
        """Returns true if the singleton instance has been created."""
        return hasattr(NameAuthority, "_instance")
        
    def install(self):
        """Installs this `NameAuthority` object as the singleton instance.

        This is normally not necessary as `instance()` will create
        an `NameAuthority` on demand, but you may want to call `install` to use
        a custom subclass of `NameAuthority`.
        """
        assert not NameAuthority.initialized()
        NameAuthority._instance = self

    def register(self, name):
        '''
        Register a name. This method raises an ExistingNameError if the name
        is already registered
        '''
        print 'registering', name
        if name in self._names:
            raise ExistingNameError('"{0}" already registered'.format(name) )
        else:
            self._names[name] = None

    def unresgister(self, name):
        '''
        Unregister the name so the same name can be registered in the future 
        '''
        print 'unregistering', name
        self._names.pop(name, None)

    def new_name(self, prefix=''):
        '''
        Creates a random uuid and register it
        :return str name
        '''
        name = str(uuid4())
        self.register(prefix + name)
        return name
    
    def clear(self):
        self._names.clear()
        
        
def register(name):
    authority = NameAuthority.instance()
    return authority.register(name)
def unregister(name):
    authority = NameAuthority.instance()
    return authority.unregister(name)
def new_name(prefix=''):
    authority = NameAuthority.instance(prefix)
    return authority.new_name()
def clear():
    authority = NameAuthority.instance()
    return authority.clear()