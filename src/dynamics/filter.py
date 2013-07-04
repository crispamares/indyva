# -*- coding: utf-8 -*-
'''
Created on 03/07/2013

@author: jmorales
'''

import uuid

from epubsub.abc_publisher import IPublisher
from epubsub.bus import Bus
from collections import OrderedDict


class DynFilter(IPublisher):
    '''
    This class maintain the state of the Filter Interactive Dynamic
    '''

    def __init__(self, name):
        '''
        @param name: unique name
        '''
        self._name = name
        self._conditions = OrderedDict()
        self._computed_sieve = None
        
        topics = ['change']
        bus = Bus(prefix= 'f.'+self._name+'.')
        IPublisher.__init__(self, bus, topics)
        
    def add_condition(self, sieve, query = None, name=None):
        ''' 
        @param sieve: Sieve is mandatory
        @param query: If the condition is explicit then a query is needed.
          Providing an explicit condition is useful for recomputing the 
          sieve if the dataset changes 
        @param name: If not provided a uuid is generated 
        '''
        name = name if name is None else str(uuid.uuid4())
        if self._conditions.has_key(name):
            raise ValueError("Already exists a condition with the name given")
        self._conditions[name] = dict(sieve=sieve, query=query)
        self._dirty()
        
    def set_condition(self, name, sieve, query=None):
        ''' 
        @param name: The key of the condition. 
        @param sieve: Sieve is mandatory
        @param query: If the condition is explicit then a query is needed.
          Providing an explicit condition is useful for recomputing the 
          sieve if the dataset changes 
        '''
        self._conditions[name] = dict(sieve=sieve, query=query)
        self._dirty()
        
    def remove_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        @param sieve: Sieve is mandatory
        @param query: If the condition is explicit then a query is needed.
          Providing an explicit condition is useful for recomputing the 
          sieve if the dataset changes 
        '''
        if self._conditions.has_key(name):
            raise ValueError("There is no condition with the given name")
        del self._conditions[name]
        self._dirty()
        
    def _dirty(self):
        self._computed_sieve = None
        
    def _compute_sieve(self):
        sieve = set()
        for c in self._conditions.values():
            sieve = sieve.union(c['sieve'])
        return sieve
    
    @property
    def sieve(self):
        '''The sieve resulting of the accumulation of every condition'''
        if self._computed_sieve is None:
            self._computed_sieve = self._compute_sieve()
        return self._computed_sieve