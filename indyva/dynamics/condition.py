# -*- coding: utf-8 -*-
'''
Created on Oct 9, 2013

@author: crispamares
'''

from sieve import ItemImplicitSieve, AttributeImplicitSieve
from external import cached
import types

from epubsub import IPublisher, Bus, pub_result
from names import INamed


class Condition(IPublisher, INamed):
    
    def __init__(self, data, name=None):
        '''
        @param data: The dataset that will be queried
        @param name: If a name is not provided, an uuid is generated
        '''        
        INamed.__init__(self, name, prefix='c:')
        self._data = data
        self._sieve = None

        topics = ['change']
        bus = Bus(prefix= '{0}:{1}:'.format('c', self.name))
        IPublisher.__init__(self, bus, topics)       

    @property
    def data(self):
        return self._data
    
    @property
    def sieve(self):
        return self._sieve
        
    def _add(self, value):
        value = set( (value,) ) if isinstance(value, types.StringTypes) \
                                else set(value)        
        self._sieve.union(value)
        self._cache_clear()
        return dict(included=list(value), excluded=[])

    def _remove(self, value):
        value = set( (value,) ) if isinstance(value, types.StringTypes) \
                                else set(value)
        self._sieve.substract(value)
        self._cache_clear()
        return dict(included=[], excluded=list(value))
    
    def _toggle_value(self, value):
        value = set( (value,) ) if isinstance(value, types.StringTypes) \
                                else set(value)
                                
        to_add = value - self.sieve.index
        to_remove = self.sieve.index.intersection(value)
        self._sieve.union(to_add)
        self._sieve.substract(to_remove)
        self._cache_clear()
        return dict(included=list(to_add), excluded=list(to_remove))
             
    def _include_all(self):
        included = self._sieve.domain - self._sieve.index 
        self._sieve.index = self._sieve.domain
        self._cache_clear()
        return dict(included=list(included), excluded=[])
    
    def _exclude_all(self):
        excluded = self._sieve.index 
        self._sieve.index = []
        self._cache_clear()
        return dict(included=[], excluded=list(excluded))
        
    def _toggle(self):
        included = self._sieve.domain - self._sieve.index 
        excluded = self._sieve.index 
        self._sieve.toggle()
        self._cache_clear()
        return dict(included=list(included), excluded=list(excluded))


        
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
        cached.invalidate(self, 'included_items')
        cached.invalidate(self, 'excluded_items')
    
    @property
    def attr(self):
        return self._attr
    
    def included_categories(self):
        return list(self._sieve.index)
     
    def excluded_categories(self):
        return list(self._sieve.domain - self._sieve.index)
    
    @cached
    def included_items(self):
        return self._data.find(self._sieve.query).index_items()
    
    @cached
    def excluded_items(self):
        return self._data.find( 
           {self._attr : {'$nin' : list(self._sieve.index) }}).index_items()

    @pub_result('change')
    def add_category(self, value):
        return self._add(value)

    @pub_result('change')
    def remove_category(self, value):
        return self._remove(value)

    @pub_result('change')
    def toggle_category(self, value):
        return self._toggle_value(value)
             
    @pub_result('change')
    def include_all(self):
        return self._include_all()
    
    @pub_result('change')    
    def exclude_all(self):
        return self._exclude_all()
        
    @pub_result('change')
    def toggle(self):
        return self._toggle()



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
    
    @pub_result('change')
    def add_attribute(self, value):
        return self._add(value)

    @pub_result('change')
    def remove_attribute(self, value):
        return self._remove(value)
    
    @pub_result('change')
    def toggle_attribute(self, value):
        return self._toggle_value(value)    
             
    @pub_result('change')
    def include_all(self):
        return self._include_all()
    
    @pub_result('change')    
    def exclude_all(self):
        return self._exclude_all()
        
    @pub_result('change')
    def toggle(self):
        return self._toggle()



