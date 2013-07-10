# -*- coding: utf-8 -*-
'''
Created on 03/07/2013

@author: jmorales
'''

import uuid

from epubsub.abc_publisher import IPublisher
from epubsub.bus import Bus
from collections import OrderedDict


class DynSelect(IPublisher):
    '''
    This class maintain the state of the Select Interactive Dynamic
    '''

    def __init__(self, name):
        '''
        @param name: unique name
        '''
        self._name = name
        self._conditions = OrderedDict()
        self._computed_reference = None
        
        topics = ['change', 'remove']
        bus = Bus(prefix= 'f.'+self._name+'.')
        IPublisher.__init__(self, bus, topics)
        
    def add_condition(self, reference, query = None, name=None):
        ''' 
        @param reference: Reference is mandatory
        @param query: If the condition is explicit then a query is needed.
          Providing an explicit condition is useful for recomputing the 
          reference if the dataset changes 
        @param name: If not provided a uuid is generated 
        '''
        name = name if name is None else str(uuid.uuid4())
        if self._conditions.has_key(name):
            raise ValueError("Already exists a condition with the name given")
        self._conditions[name] = dict(reference=reference, query=query)
        self._dirty()
        
        self._bus.publish('change', name)
        
    def set_condition(self, name, reference, query=None):
        ''' 
        @param name: The key of the condition. 
        @param reference: Reference is mandatory
        @param query: If the condition is explicit then a query is needed.
          Providing an explicit condition is useful for recomputing the 
          reference if the dataset changes 
        '''
        self._conditions[name] = dict(reference=reference, query=query)
        self._dirty()
        
        self._bus.publish('change', name)
        
    def remove_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        @param reference: Reference is mandatory
        @param query: If the condition is explicit then a query is needed.
          Providing an explicit condition is useful for recomputing the 
          reference if the dataset changes 
        '''
        if self._conditions.has_key(name):
            raise ValueError("There is no condition with the given name")
        del self._conditions[name]
        self._dirty()
        
        self._bus.publish('remove', name)

    def is_empty(self):
        return len(self._conditions) == 0
    
    @property
    def ref(self):
        '''The reference resulting of the accumulation of every condition.
        A reference is a set of indices or None if there are no conditions'''
        if self._computed_reference is None:
            self._computed_reference = self._compute_reference()
        return self._computed_reference

    def query(self, index):
        '''The query resulting of the accumulation of every condition.
        @param index: A string or list of strings'''
        if self.is_empty():
            return {}
        if self._computed_reference is None:
            self._computed_reference = self._compute_reference()
        if isinstance(index, list):
            NotImplementedError('Multi Index is not supported yet')
        return { index : {'$in': list(self._computed_reference)} }
        
    def _dirty(self):
        self._computed_reference = None
        
    def _compute_reference(self):
        if self.is_empty():
            return None
        reference = set()
        for c in self._conditions.values():
            reference = reference.union(c['reference'])
        return reference
    
