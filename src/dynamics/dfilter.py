# -*- coding: utf-8 -*-
'''
Created on 03/07/2013

@author: jmorales
'''

from epubsub.abc_publisher import IPublisher
from epubsub.bus import Bus

from sieve import ItemSieve, AttrSieve

class DynFilter(IPublisher):
    '''
    This class maintain the state of the Filter Interactive Dynamic
    
    All references from each conditions are aggregated with Intersection set 
    operation 
    '''

    def __init__(self, name):
        '''
        @param name: unique name
        '''
        self._name = name
        self._item_sieve = ItemSieve()
        self._attr_sieve = AttrSieve()
        
        topics = ['change', 'remove']
        bus = Bus(prefix= 'f.'+self._name+'.')
        IPublisher.__init__(self, bus, topics)
        
    def add_item_condition(self, reference, query = None, name=None):
        ''' 
        @param reference: Reference is mandatory
        @param query: If the condition is explicit then a query is needed.
          Providing an explicit condition is useful for recomputing the 
          reference if the dataset changes 
        @param name: If not provided a uuid is generated 
        '''
        self._item_sieve.add_condition(reference, query, name)
        self._bus.publish('change', name)

    def add_attr_condition(self, projection, name=None):
        ''' 
        @param projection: Projection is mandatory
        @param name: If not provided a uuid is generated 
        '''
        self._attr_sieve.add_condition(projection, name)
        self._bus.publish('change', name)
        
        
    def set_item_condition(self, name, reference, query=None):
        ''' 
        @param name: The key of the condition. 
        @param reference: Reference is mandatory
        @param query: If the condition is explicit then a query is needed.
          Providing an explicit condition is useful for recomputing the 
          reference if the dataset changes 
        '''
        self._item_sieve.set_condition(name, reference, query)       
        self._bus.publish('change', name)

    def set_attr_condition(self, name, projection):
        ''' 
        @param name: The key of the condition. 
        @param projection: Projection is mandatory
        '''
        self._attr_sieve.set_condition(name, projection)       
        self._bus.publish('change', name)
        
    def remove_item_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        self._item_sieve.remove_condition(name)
        self._bus.publish('remove', name)

    def remove_attr_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        self._attr_sieve.remove_condition(name)
        self._bus.publish('remove', name)

    def has_item_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        return self._item_sieve.has_condition(name)

    def has_attr_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        return self._attr_sieve.has_condition(name)
        

    def is_empty(self):
        return self._item_sieve.is_empty() and self._attr_sieve.is_empty()
    
    @property
    def ref(self):
        '''The reference resulting of the accumulation of every item condition.
        A reference is a set of indices or None if there are no item conditions'''
        return self._item_sieve.ref

    @property
    def projection(self):
        '''The projection resulting of the accumulation of every condition.
        A projection is a dict of { 'attr_name' -> Bool } or None if there are no conditions'''
        return self._attr_sieve.projection
    
    def query(self, index):
        '''The query resulting of the accumulation of both item and attr conditions.
        @param index: A string or list of strings
        @return: (query, projection)'''
        return self._item_sieve.query(index) , self._attr_sieve.projection
            
