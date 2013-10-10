# -*- coding: utf-8 -*-
'''
Created on Oct 9, 2013

@author: crispamares
'''

from sieve import ItemImplicitSieve, AttributeImplicitSieve
from external import lru_cache
import types
import uuid


class Condition(object):
    
    def __init__(self, data, name=None):
        '''
        @param data: The dataset that will be queried
        @param name: If a name is not provided, an uuid is generated
        '''        
        self._data = data
        self.name = name if name is not None else str(uuid.uuid4())
        self._sieve = None

    @property
    def data(self):
        return self._data
    
    @property
    def sieve(self):
        return self._sieve
        
        


        
class CategoricalCondition(Condition):
    
    def __init__(self, data, attr, categories=[], name=None, bins=None):
        '''
        :param data: The dataset that will be queried
        :param attr: The attribute that will be used as the category 
        :param categories: The categories initially included 
        :param name: If a name is not provided, an uuid is generated
        :param bins: If provided, the attribute will be coerced to be
        categorical by grouping in this number of bins 
        '''
        Condition.__init__(self, data, name)
        self._attr = attr
        self._bins = bins
        
        if data.schema.attributes[attr].attribute_type != 'CATEGORICAL':
            raise NotImplementedError('Bins not yet implemented')
        if bins is not None:
            raise NotImplementedError('Bins not yet implemented')
        
        self._sieve = ItemImplicitSieve(data, categories, data_index=attr)

    def _cache_clear(self):
        self.included_items.cache_clear()
        self.excluded_items.cache_clear()
    
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
             
    def include_all(self):
        self._sieve.index = self._sieve.domain
        self._cache_clear()
        
    def exclude_all(self):
        self._sieve.index = []
        self._cache_clear()
        
    def toggle(self):
        self._sieve.toggle()
        self._cache_clear()




class AttributeCondition(Condition):
    def __init__(self, data, attributes=[], name=None):
        '''
        :param data: The dataset that will be queried
        :param attributes: The attributes initially included
        :param name: If a name is not provided, an uuid is generated
        '''
        Condition.__init__(self, data, name)
        
        self._sieve = AttributeImplicitSieve(data, attributes)

    def included_attributes(self):
        return list(self._sieve.index)
     
    def excluded_attributes(self):
        return list(self._sieve.domain - self._sieve.index)
    
    def add_category(self, value):
        if isinstance(value, types.StringTypes):
            value = set( (value,) )
        self._sieve.union(set(value))

    def remove_category(self, value):
        if isinstance(value, types.StringTypes):
            value = set( (value,) )
        self._sieve.substract(value)
             
    def include_all(self):
        self._sieve.index = self._sieve.domain
        
    def exclude_all(self):
        self._sieve.index = []
        
    def toggle(self):
        self._sieve.toggle()



