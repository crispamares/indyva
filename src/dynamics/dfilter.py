# -*- coding: utf-8 -*-
'''
Created on 03/07/2013

@author: jmorales
'''

from epubsub.abc_publisher import IPublisher
from epubsub.bus import Bus

from sieve import (SieveSet, AttributeImplicitSieve, ItemSievesFactory)

class DynFilter(IPublisher):
    '''
    This class maintain the state of the Filter Interactive Dynamic
    
    All references from each conditions are aggregated with Intersection set 
    operation (a.k.a. AND)
    '''

    def __init__(self, name, data):
        '''
        @param name: unique name
        @param data: the dataset that is going to suffer the filters 
        '''
        self._name = name
        self._data = data
        self._sieves = SieveSet()

        topics = ['change', 'remove']
        bus = Bus(prefix= 'f.'+self._name+'.')
        IPublisher.__init__(self, bus, topics)
        
    def add_condition(self, condition, name=None):
        '''Every condition has to share the same data as this dynamic otherwise
         a ValueError is raised
         
        @param condition: A condition could be either an ImplicitSieve or an 
        ExplicitSieve.  
        @param name: If not provided a uuid is generated 
        '''
        if condition.data != self._data:
            raise ValueError("Condition has {0} dataset, {1} expected"
                             .format(condition.data.name, self._data.name))
        self._sieves.add_condition(condition, name)
        self._bus.publish('change', name)

    def set_condition(self, name, condition):
        '''Every condition has to share the same data as this dynamic otherwise
         a ValueError is raised
        
        @param name: The key of the condition
        @param condition: A condition could be either an ImplicitSieve or an 
        ExplicitSieve.  
        
        '''
        if condition.data != self._data:
            raise ValueError("Condition has {0} dataset, {1} expected"
                             .format(condition.data.name, self._data.name))
        self._sieves.set_condition(name, condition)
        self._bus.publish('change', name)
        
    def add_item_condition(self, reference=None, query = None, name=None):
        ''' 
        You can create an implicit (by giving the reference) or explicit (by 
        giving the query) condition 
        @param reference: Reference is a list of item keys
        @param query: Providing an explicit condition is useful for recomputing
         the reference if the dataset changes 
        @param name: If not provided a uuid is generated 
        '''
        condition = ItemSievesFactory.from_ref_and_query(self._data, reference, query)
        self._sieves.add_condition(condition, name)
        self._bus.publish('change', name)

    def add_attr_condition(self, attr_reference, name=None):
        ''' 
        @param attr_reference: is a list of attribute names
        @param name: If not provided a uuid is generated 
        '''
        condition = AttributeImplicitSieve(self._data, attr_reference)
        self._sieves.add_condition(condition, name)
        self._bus.publish('change', name)
        
        
    def set_item_condition(self, name, reference=None, query=None):
        ''' 
        @param name: The key of the condition. 
        @param reference: Reference is a list of item keys
        @param query: Providing an explicit condition is useful for recomputing
         the reference if the dataset changes 
        '''
        condition = ItemSievesFactory.from_ref_and_query(self._data, reference, query)
        self._sieves.set_condition(name, condition)
        self._bus.publish('change', name)

    def set_attr_condition(self, name, attr_reference):
        ''' 
        @param name: The key of the condition. 
        @param attr_reference: is a list of attribute names
        '''
        condition = AttributeImplicitSieve(self._data, attr_reference)
        self._sieves.set_condition(name, condition)       
        self._bus.publish('change', name)
        
    def remove_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        self._sieves.remove_condition(name)
        self._bus.publish('remove', name)

    def has_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        return self._sieves.has_condition(name)
        
    def is_empty(self):
        return self._sieves.is_empty() 
    
    @property
    def reference(self):
        '''The reference resulting of the accumulation of every item condition.
        A reference is a set of indices or None if there are no item conditions
        '''
        return self._sieves.reference

    @property
    def projection(self):
        '''The projection resulting of the accumulation of every attribute 
        condition.
        A projection is a dict of { 'attr_name' -> Bool } or None if there are 
        no conditions'''
        return self._sieves.projection
    
    @property
    def query(self):
        '''The query resulting of the accumulation of item conditions.
        '''
        return self._sieves.query
    
    @property
    def view_args(self):
        '''The view_args, that groups the query and the projection 
        @return: dict(query=>query, projection=>projection)
        '''
        return dict(query = self.query, projection= self.projection) 
    


            
