# -*- coding: utf-8 -*-
'''
Created on Oct 9, 2013

@author: crispamares
'''
from __future__ import division

import types

from indyva.epubsub import IPublisher, Bus, pub_result
from indyva.names import INamed
from indyva.external import cached
from .sieve import ItemImplicitSieve, AttributeImplicitSieve, ItemExplicitSieve

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
    
    def _value_in_a_set(self, value):
        the_set = set( (value,) ) if isinstance(value, (types.StringTypes, types.IntType)) \
                                else set(value)        
        return the_set
        
    def _add(self, value):
        value = self._value_in_a_set(value)        
        self._sieve.union(value)
        self._cache_clear()
        return dict(included=list(value), excluded=[])

    def _remove(self, value):
        value = self._value_in_a_set(value)        
        self._sieve.substract(value)
        self._cache_clear()
        return dict(included=[], excluded=list(value))
    
    def _toggle_value(self, value):
        value = self._value_in_a_set(value)        
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




class RangeCondition(Condition):
    def __init__(self, data, attr, cond_range={}, domain={}, name=None):
        '''
        :param data: The dataset that will be queried
        :param attr: The attribute that will compared with cond_range values. 
        :param cond_range: {min: val, max: val} The maximum and minimum values 
            of the condition.
            All items whose attr value is inside the range are considered as
            included.
        :param domain: {min: val, max: val} The domain of the RangeCondition 
            are the maximum and minimum values that the range can get.
        :param name: If a name is not provided, an uuid is generated
        '''
        Condition.__init__(self, data, name)
        self._attr = attr

        #=======================================================================
        #        Handle domain
        #=======================================================================
        if not ('max' in domain and 'min' in domain):
            raise ValueError("Error creating RangeCondition: " +
                             "domain must be a dict with min and max keys" +
                             " this was provided: " + str(cond_range))
        if len(domain == 0):
            # TODO: Use the max/min of the new schema
            domain = data.aggregate([{'$group': 
                                      {'_id':"$"+attr, 
                                       'min': {'$min': "$"+attr},
                                       'max': {'$max': "$"+attr}}}]).get_data()

        domain = {'min':domain['min'], 'max':domain['max']}
        self._domain = domain
        
        #=======================================================================
        #         Handle cond_range
        #=======================================================================
        if not ('max' in cond_range and 'min' in cond_range):
            raise ValueError("Error creating RangeCondition: " +
                             "cond_range must be a dict with min and max keys" +
                             " this was provided: " + str(cond_range))
        if len(cond_range == 0):
            cond_range = self._domain
        cond_range = {'min':cond_range['min'], 'max':cond_range['max']}
        self._cond_range = cond_range
        
        query = self._generate_query()
        self._sieve = ItemExplicitSieve(data, query)


    def _generate_query(self):
        return {'$and': [{"gte": self._cond_range['min']},
                         {"lte": self._cond_range['max']} ]}
        
    def _to_relative(self, abs_val):
        return ((abs_val - self._domain['min']) / 
                (self._domain['max'] - self._domain['min'])) 

    def _to_absolute(self, rel_val):
        return ((self._domain['max'] - self._domain['min']) * rel_val 
                + self._domain['min']) 

    @property
    def attr(self):
        return self._attr
        
    @property
    def range(self):
        '''
        :return: {min, max, relative_min, relative_max} Relative values are
            between 0 and 1
        '''
        result = {}.update(self._cond_range)
        result['relative_min'] = self._to_relative(self._cond_range['min'])
        result['relative_max'] = self._to_relative(self._cond_range['max'])
        return self.result
        
    @property
    def domain(self):
        return self._domain
                 
    @pub_result('change')
    def include_all(self):
        return self._include_all()



