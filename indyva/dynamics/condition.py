# -*- coding: utf-8 -*-
'''
Created on Oct 9, 2013

@author: crispamares
'''
from __future__ import division
import __builtin__
import types

from indyva.epubsub import IPublisher, Bus, pub_result
from indyva.core.names import INamed
from indyva.core.grava import IDefined, register
from indyva.external import cached
from .sieve import ItemImplicitSieve, AttributeImplicitSieve, ItemExplicitSieve


class Condition(IPublisher, INamed, IDefined):

    def __init__(self, data, name=None, enabled=True, prefix=''):
        '''
        :param data: The dataset that will be queried
        :param str name: If a name is not provided, an uuid is generated
        :param bool enabled: If the condition is disabled it will be ignored in the
            computation of the ConditionSet combination
        :param str prefix: Prepended to the name creates the oid
        '''
        INamed.__init__(self, name, prefix=prefix)
        self._data = data
        self._sieve = None
        self._enabled = enabled

        topics = ['change', 'enable']
        bus = Bus(prefix= '{0}{1}:'.format(prefix, self.name))
        IPublisher.__init__(self, bus, topics)

    @property
    def data(self):
        return self._data

    @property
    def sieve(self):
        return self._sieve

    @property
    def enabled(self):
        return self._enabled

    @property
    def grammar(self):
        return dict(name = self.name,
                    data = self.data.name,
                    enabled = self.enabled)

    @pub_result('enable')
    def enable(self, enable=True):
        self._enabled = enable
        return self._enabled

    @pub_result('enable')
    def disable(self, enable=False):
        self._enabled = enable
        return self._enabled

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



@register('categorical')
class CategoricalCondition(Condition):

    def __init__(self, data, attr, categories=None, name=None, bins=None, enabled=True, prefix=''):
        '''
        :param data: The dataset that will be queried
        :param attr: The attribute that will be used as the category
        :param categories: The categories initially included
        :param name: If a name is not provided, an uuid is generated
        :param bins: If provided, the attribute will be coerced to be
                     categorical by grouping in this number of bins
        :param str prefix: Prepended to the name creates the oid
        '''
        Condition.__init__(self, data, name, enabled=enabled, prefix=prefix)
        self._attr = attr
        self._bins = bins

        if data.schema.attributes[attr].attribute_type != 'CATEGORICAL':
            raise NotImplementedError('Bins not yet implemented')
        if bins is not None:
            raise NotImplementedError('Bins not yet implemented')

        categories = [] if categories is None else categories
        self._sieve = ItemImplicitSieve(data, categories, data_index=attr)

    def _cache_clear(self):
        cached.invalidate(self, 'included_items')
        cached.invalidate(self, 'excluded_items')

    @property
    def attr(self):
        return self._attr

    @property
    def grammar(self):
        grammar = Condition.grammar.fget(self)
        grammar.update({'type': 'categorical',
                        'attr': self.attr,
                        'bins': self._bins,
                        'included_categories': self.included_categories(),
                        'excluded_categories': self.excluded_categories()})
        return grammar

    @classmethod
    def build(cls, grammar, objects):
        dataset = objects[grammar['data']]
        self = cls(data=dataset,
                   attr=grammar['attr'],
                   categories=grammar['included_categories'],
                   name=grammar['name'],
                   bins=grammar['bins'],
                   enabled=grammar['enabled'])
        return self

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



@register('attribute')
class AttributeCondition(Condition):
    def __init__(self, data, attributes=None, name=None, enabled=True, prefix=''):
        '''
        :param data: The dataset that will be queried
        :param attributes: The attributes initially included
        :param name: If a name is not provided, an uuid is generated
        :param str prefix: Prepended to the name creates the oid
        '''
        Condition.__init__(self, data, name, enabled=enabled, prefix=prefix)

        attributes = [] if attributes is None else attributes
        self._sieve = AttributeImplicitSieve(data, attributes)

    @property
    def grammar(self):
        grammar = Condition.grammar.fget(self)
        grammar.update({'type': 'attribute',
                        'included_attributes': self.included_attributes(),
                        'excluded_attributes': self.excluded_attributes()})
        return grammar

    @classmethod
    def build(cls, grammar, objects):
        dataset = objects[grammar['data']]
        self = cls(data=dataset,
                   attributes=grammar['included_attributes'],
                   name=grammar['name'],
                   enabled=grammar['enabled'])
        return self

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


@register('range')
class RangeCondition(Condition):
    def __init__(self, data, attr, range=None, domain=None, name=None, enabled=True, prefix=''):
        '''
        This Condition handles NaN values.

        :param data: The dataset that will be queried
        :param attr: The attribute that will compared with range values.
        :param range: {min: val, max: val} The maximum and minimum values
            of the condition.
            All items whose attr value is inside the range are considered as
            included.
        :param domain: {min: val, max: val} The domain of the RangeCondition
            are the maximum and minimum values that the range can get.
        :param name: If a name is not provided, an uuid is generated
        :param str prefix: Prepended to the name creates the oid
        '''
        Condition.__init__(self, data, name, enabled=enabled, prefix=prefix)
        self._attr = attr

        #=======================================================================
        #        Handle domain
        #=======================================================================
        if domain == None:
            # TODO: Use the max/min of the new schema
            domain = data.aggregate([{'$match': {attr: {'$type': 1}}},  # Only numbers
                                     {'$group':
                                      {'_id': {},
                                       'min': {'$min': "$"+attr},
                                       'max': {'$max': "$"+attr}}}]).get_data()[0]
        elif (not isinstance(domain, dict)
              or not ('max' in domain and 'min' in domain)):
            raise ValueError("Error creating RangeCondition: " +
                             "domain must be a dict with min and max keys" +
                             " this was provided: " + str(domain))

        domain = {'min':domain['min'], 'max':domain['max']}
        self._domain = domain

        #=======================================================================
        #         Handle range
        #=======================================================================
        if range == None:
            range = self._domain
        elif (not isinstance(range, dict)
              or not ('max' in range and 'min' in range)):
            raise ValueError("Error creating RangeCondition: " +
                             "range must be a dict with min and max keys" +
                             " this was provided: " + str(range))

        range = {'min': max(range['min'], domain['min']),
                      'max': min(range['max'], domain['max'])}
        self._range = range

        query = self._generate_query()
        self._sieve = ItemExplicitSieve(data, query)


    def _cache_clear(self):
        cached.invalidate(self, 'included_items')
        cached.invalidate(self, 'excluded_items')

    def _generate_query(self):
        return {'$and': [{self._attr: {"$gte": self._range['min']}},
                         {self._attr: {"$lte": self._range['max']}} ]}

    def _to_relative(self, abs_val):
        return ((abs_val - self._domain['min']) /
                (self._domain['max'] - self._domain['min']))

    def _to_absolute(self, rel_val):
        return ((self._domain['max'] - self._domain['min']) * rel_val
                + self._domain['min'])

    @property
    def grammar(self):
        grammar = Condition.grammar.fget(self)
        grammar.update({'type': 'range',
                        'attr': self.attr,
                        'range': self.range,
                        'domain': self.domain})
        return grammar

    @classmethod
    def build(cls, grammar, objects):
        dataset = objects[grammar['data']]
        self = cls(data=dataset,
                   attr=grammar['attr'],
                   range=grammar['range'],
                   domain=grammar['domain'],
                   name=grammar['name'],
                   enabled=grammar['enabled'])
        return self

    @property
    def attr(self):
        return self._attr

    @property
    def range(self):
        '''
        :return: {min, max, relative_min, relative_max} Relative values are
            between 0 and 1
        '''
        result = {}
        result.update(self._range)
        result['relative_min'] = self._to_relative(self._range['min'])
        result['relative_max'] = self._to_relative(self._range['max'])
        return result

    @property
    def domain(self):
        return self._domain

    @cached
    def included_items(self):
        return self._data.find(self._sieve.query).index_items()

    @cached
    def excluded_items(self):
        not_query = {'$or': [{self._attr: {"$lt": self._range['min']}},
                             {self._attr: {"$gt": self._range['max']}} ]}

        return self._data.find(not_query).index_items()

    @pub_result('change')
    def include_all(self):
        self._cache_clear()
        self._range.update(self._domain)
        self._sieve.query = self._generate_query()

        included = self._sieve.domain - self._sieve.index
        excluded = self._sieve.index
        return dict(included=list(included), excluded=list(excluded))

    @pub_result('change')
    def set_range(self, min=None, max=None, relative=False):
        '''
        :param min: The lower limit of the range
        :param max: The upper limit of the range
        :param relative: If True then min and max are provided as 0 to 1 values
            otherwise are absolute values.
        '''
        if min is None and max is None:
            raise ValueError('You must set at least the min or the max')
        if min is not None:
            if not relative:
                self._range['min'] = min
            else:
                self._range['min'] = self._to_absolute(__builtin__.max(min, 0))
        if max is not None:
            if not relative:
                self._range['max'] = max
            else:
                self._range['max'] = self._to_absolute(__builtin__.min(max, 1))

        self._cache_clear()
        old_index = self._sieve.index
        self._sieve.query = self._generate_query()

        included = self._sieve.index - old_index
        excluded = old_index - self._sieve.index
        return dict(included=list(included), excluded=list(excluded))



@register('query')
class QueryCondition(Condition):
    def __init__(self, data, query=None, name=None, enabled=True, prefix=''):
        '''
        :param data: The dataset that will be queried
        :param query: A MongoDB query
        :param name: If a name is not provided, an uuid is generated
        :param str prefix: Prepended to the name creates the oid
        '''
        Condition.__init__(self, data, name, enabled=enabled, prefix=prefix)

        self._query = query if query is not None else {}
        self._attr = self._data.index
        self._sieve = ItemExplicitSieve(data, self._query)


    def _cache_clear(self):
        cached.invalidate(self, 'included_items')
        cached.invalidate(self, 'excluded_items')

    @property
    def grammar(self):
        grammar = Condition.grammar.fget(self)
        grammar.update({'type': 'query',
                        'attr': self.attr,
                        'query': self.query})
        return grammar

    @classmethod
    def build(cls, grammar, objects):
        dataset = objects[grammar['data']]
        self = cls(data=dataset,
                   query=grammar['query'],
                   name=grammar['name'],
                   enabled=grammar['enabled'])
        return self

    @property
    def attr(self):
        return self._attr

    @property
    def query(self):
        return self._query

    @cached
    def included_items(self):
        return self._data.find(self._sieve.query).index_items()

    @cached
    def excluded_items(self):
        return self._data.find(
           {self._attr : {'$nin' : list(self._sieve.index) }}).index_items()

    @pub_result('change')
    def set_query(self, query):
        '''
        :param query: A MongoDB query
        '''
        self._query = query
        self._cache_clear()
        old_index = self._sieve.index
        self._sieve.query = query

        included = self._sieve.index - old_index
        excluded = old_index - self._sieve.index
        return dict(included=list(included), excluded=list(excluded))
