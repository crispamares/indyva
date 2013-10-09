# -*- coding: utf-8 -*-
'''
Created on Oct 9, 2013

@author: crispamares
'''

from sieve import ItemImplicitSieve
from external import lru_cache
import types

class CategoricalCondition(object):
    
    def __init__(self, data, attr, name=None, bins=None):
        '''
        @param data: The dataset that will be queried
        @param attr: The attribute that will be used as the category  
        @param name: The id 
        @param bins: If provided, the attribute will be coerced to be
        categorical by grouping in this number of bins 
        '''
        self._data = data
        self._attr = attr
        self._bins = bins
        self._name = name

        if data.schema.attributes[attr].attribute_type != 'CATEGORICAL':
            raise NotImplementedError('Bins not yet implemented')
        if bins is not None:
            raise NotImplementedError('Bins not yet implemented')
        
        self._sieve = ItemImplicitSieve(data, [], data_index=attr)

    def _cache_clear(self):
        self.included_items.cache_clear()
        self.excluded_items.cache_clear()

    @property
    def data(self):
        return self._data
    
    @property
    def attr(self):
        return self._attr
    
    def included_categories(self):
        return list(self._sieve.index)
     
    def excluded_categories(self):
        return list(self._sieve.domain - self._sieve.index)
    
    @lru_cache(1)
    def included_items(self):
        return self._data.find(self._sieve.query).index_items()
    
    @lru_cache(1)
    def excluded_items(self):
        return self._data.find( 
           {self._attr : {'$nin' : list(self._sieve.index) }}).index_items()

    def add_category(self, value):
        if isinstance(value, types.StringTypes):
            value = set( (value,) )
        self._sieve.union(set(value))
        self._cache_clear()

    def remove_category(self, value):
        if isinstance(value, types.StringTypes):
            value = set( (value,) )
        self._sieve.substract(value)
        self._cache_clear()
             
    def incude_all(self):
        self._sieve.index = self._sieve.domain
        self._cache_clear()
        
    def exclude_all(self):
        self._sieve.index = []
        self._cache_clear()
        
    def toggle(self):
        self._sieve.toggle()
        self._cache_clear()
