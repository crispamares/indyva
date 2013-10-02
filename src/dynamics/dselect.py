# -*- coding: utf-8 -*-
'''
Created on 03/07/2013

@author: jmorales
'''

from epubsub.abc_publisher import IPublisher
from epubsub.bus import Bus

from sieve import (SieveSet, ItemSievesFactory)

class DynSelect(IPublisher):
    '''
    This class maintain the state of the Select Interactive Dynamic
    
    All references from each conditions are aggregated with Union set operation 
    '''

    def __init__(self, name, data):
        '''
        @param name: unique name
        '''
        self._name = name
        self._sieves = SieveSet(setop='OR')
        self._data = data
        
        topics = ['change', 'remove']
        bus = Bus(prefix= 'f.'+self._name+'.')
        IPublisher.__init__(self, bus, topics)
        
    def add_condition(self, reference_query_condition, name=None):
        '''Every condition has to share the same data as this dynamic otherwise
         a ValueError is raised
         
        @param reference_query_condition: 
           - Could be a reference (list or set)
           - Could be a query (dict)   
           - Could be a condition (ImplicitSieve or ExplicitSieve)           
        @param name: If not provided a uuid is generated 
        '''
        condition = ItemSievesFactory.from_rqs(self._data, reference_query_condition)
        self._sieves.add_condition(condition, name)
        self._bus.publish('change', name)
        
    def set_condition(self, name, reference_query_condition):
        '''Every condition has to share the same data as this dynamic otherwise
         a ValueError is raised
         
        @param name: The key of the condition 
        @param reference_query_condition: 
           - Could be a reference (list or set)
           - Could be a query (dict)   
           - Could be a condition (ImplicitSieve or ExplicitSieve)           
        '''
        condition = ItemSievesFactory.from_rqs(self._data, reference_query_condition)
        self._sieves.set_condition(name, condition)
        self._bus.publish('change', name)
        
    def remove_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        self._sieves.remove_condition(name)
        self._bus.publish('remove', name)

    def is_empty(self):
        return self._sieves.is_empty()
    
    @property
    def reference(self):
        '''The reference resulting of the accumulation of every condition.
        A reference is a set of indices or [] if there are no conditions'''
        return self._sieves.reference
    
    @property
    def query(self):
        '''The query resulting of the accumulation of every condition.
        '''
        return self._sieves.query
            
