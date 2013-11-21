# -*- coding: utf-8 -*-
'''
Created on 20/11/2013

@author: jmorales
'''

from weakref import WeakValueDictionary

class Showcase(object):
    '''
    This class enables other classes to translate names to actual objects, 
    previously registered
    '''

    def __init__(self):
        self._objects = WeakValueDictionary()
        self._cases = WeakValueDictionary()
        
    @staticmethod
    def instance():
        """Returns a global `Showcase` instance. 
        
        :warning: Not ThreadSafe.
        """
        if not hasattr(Showcase, "_instance"):        
            Showcase._instance = Showcase()
        return Showcase._instance

    @staticmethod
    def initialized():
        """Returns true if the singleton instance has been created."""
        return hasattr(Showcase, "_instance")
        
    def install(self):
        """Installs this `Showcase` object as the singleton instance.

        This is normally not necessary as `instance()` will create
        an `Showcase` on demand, but you may want to call `install` to use
        a custom subclass of `Showcase`.
        """
        assert not Showcase.initialized()
        Showcase._instance = self    
        
    def get(self, full_name):
        '''
        :param str full_name: the full_name registered in the NameAuthority 
        '''
        return self._objects.get(full_name)    
    
    def put(self, instance):
        '''
        :param INamed full_name: the exposed object.
        '''
        self._objects[instance.full_name] = instance  
        
    def get_case(self, name):
        case = self._cases.get(name)
        if case is None:
            case = self._cases[name] = Case()
        return case
    
class Case(dict):
    def __setitem__(self, *args, **kwargs):
        Showcase.instance().put(args[1])
        return dict.__setitem__(self, *args, **kwargs)
