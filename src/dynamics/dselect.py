# -*- coding: utf-8 -*-
'''
Created on 03/07/2013

@author: jmorales
'''

from epubsub.abc_publisher import IPublisher
from epubsub.bus import Bus

from sieve import ItemSieve

class DynSelect(IPublisher):
    '''
    This class maintain the state of the Select Interactive Dynamic
    '''

    def __init__(self, name):
        '''
        @param name: unique name
        '''
        self._name = name
        self._item_sieve = ItemSieve()
        
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
        self._item_sieve.add_condition(reference, query, name)
        self._bus.publish('change', name)
        
    def set_condition(self, name, reference, query=None):
        ''' 
        @param name: The key of the condition. 
        @param reference: Reference is mandatory
        @param query: If the condition is explicit then a query is needed.
          Providing an explicit condition is useful for recomputing the 
          reference if the dataset changes 
        '''
        self._item_sieve.set_condition(name, reference, query)       
        self._bus.publish('change', name)
        
    def remove_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        self._item_sieve.remove_condition(name)
        self._bus.publish('remove', name)

    def is_empty(self):
        return self._item_sieve.is_empty()
    
    @property
    def ref(self):
        '''The reference resulting of the accumulation of every condition.
        A reference is a set of indices or None if there are no conditions'''
        return self._item_sieve.ref

    def query(self, index):
        '''The query resulting of the accumulation of every condition.
        @param index: A string or list of strings'''
        return self._item_sieve.query(index)
            
