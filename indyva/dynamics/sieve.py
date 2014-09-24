# -*- coding: utf-8 -*-
'''
Created on 10/07/2013

@author: jmorales
'''
from collections import OrderedDict
import uuid
from copy import copy

from indyva.external import lazy
from indyva.external.cached import cached


class ImplicitSieve(object):

    def __init__(self, data, index, data_index=None):
        self._data = data
        self._domain = None
        self._index = set(index)
        self._data_index = data_index if data_index else self._data.index

    @property
    def data(self):
        return self._data
    @property
    def domain(self):
        raise NotImplemented()
    @property
    def index(self):
        return self._index
    @index.setter
    def index(self, index):
        self._index = set(index)
        self._cache_clear()
    @property
    def query(self):
        raise NotImplemented()
    @property
    def items(self):
        raise NotImplemented()

    def _cache_clear(self):
        pass

    def union(self, index):
        self._index = self.index.union(set(index))
        self._cache_clear()
        return self

    def substract(self, index):
        self._index = self.index - set(index)
        self._cache_clear()
        return self

    def toggle(self):
        self._index = self.domain - self.index
        self._cache_clear()
        return self

    def intersect(self, index):
        self._index.intersection_update(set(index))
        self._cache_clear()
        return self

    def to_explicit(self):
        raise NotImplemented()

    def to_implitic(self):
        return self

    def __eq__(self, other):
        return self.domain == other.domain and self._index == other.index

    def __repr__(self):
        return 'Sieve: ' + str(self.index)



class ItemImplicitSieve(ImplicitSieve):

    @property
    def domain(self):
        if self._domain is None:
            self._domain = set(self._data.distinct(self._data_index))
        return self._domain
    @property
    def query(self):
        return { self._data_index : {'$in': list(self._index)} }

    @lazy
    def items(self):
        return set(self.data.find(self.query).index_items())

    def _cache_clear(self):
        lazy.invalidate(self, 'items')


    def to_explicit(self):
        query = { self._data_index : {'$in': list(self._index)} }
        return ItemExplicitSieve(self.data, query)


class AttributeImplicitSieve(ImplicitSieve):

    @property
    def domain(self):
        if self._domain is None:
            self._domain = set(self.data.column_names())
        return self._domain
    @property
    def projection(self):
        if len(self.index) == 0:
            return {}
        return { column : True for column in self.domain if column in self.index}


class ItemExplicitSieve(object):
    def __init__(self, data, query, data_index=None):
        self._data = data
        self._domain = None
        self._query = query
        self._data_index = data_index if data_index else self._data.index

    @property
    def data(self):
        return self._data
    @property
    def domain(self):
        if self._domain is None:
            self._domain = set(self.data.distinct(self._data_index))
        return self._domain
    @property
    def query(self):
        return copy(self._query)
    @query.setter
    def query(self, query):
        self._query = copy(query)
        self._cache_clear()
    @property
    def index(self):
        return self.to_implicit().index
    @lazy
    def items(self):
        return set(self.data.find(self.query).index_items())

    def _cache_clear(self):
        lazy.invalidate(self, 'items')
        cached.invalidate(self, 'to_implicit')

    def union(self, query):
        self.query = {'$or': [self._query, query]}
        return self

    def substract(self, query):
        self.query = {'$and': [self._query, {"$nor": [query]}]}
        return self

    def toggle(self):
        self.query = {'$nor': [self._query]}
        return self

    def intersect(self, query):
        self.query = {'$and': [self._query, query]}
        return self

    @cached
    def to_implicit(self):
        domain = self.domain
        index = self._data.find(self._query).distinct(self._data_index)
        self._implicit_form = ImplicitSieve(domain, index, self._data_index)
        return self._implicit_form

    def to_explicit(self):
        return self

    def __eq__(self, other):
        return self.data is other.data and self.query == other.query

    def __repr__(self):
        return 'Sieve: ' + str(self.query)

class ItemSievesFactory(object):

    @staticmethod
    def from_ref_and_query(data, reference=None, query=None):
        '''
        Both reference and query must not be provided at the same time

        :param data: DataSet of the sieve
        :param reference: A list of item keys
        :param query: An explicit query
        '''
        if reference is not None and query is not None:
            raise ValueError('Both reference and query params provided')
        if reference is not None:
            sieve = ItemImplicitSieve(data, reference)
        if query is not None:
            sieve = ItemExplicitSieve(data, query)
        return sieve

    @staticmethod
    def from_rqs(data, reference_query_sieve):
        '''
        :param reference_query_sieve:
           - Could be a sieve (ImplicitSieve or ExplicitSieve)
           - Could be a reference (list or set)
           - Could be a query (dict)
        :param name: If not provided a uuid is generated
        '''
        if isinstance(reference_query_sieve, (list, set)):
            reference = reference_query_sieve
            sieve = ItemImplicitSieve(data, reference)
        elif isinstance(reference_query_sieve, dict):
            query = reference_query_sieve
            sieve = ItemExplicitSieve(data, query)
        elif isinstance(reference_query_sieve, (ItemImplicitSieve, ItemExplicitSieve)):
            sieve = reference_query_sieve
            if sieve.data != data:
                raise ValueError("Sieve has '{0}' dataset, {1} expected"
                                 .format(sieve.data.name, data.name))
        return sieve

class SieveSet(object):
    def __init__(self, data, setop='AND'):
        ''':param setop: The set operation. AND or OR'''
        self._item_implicit_sieves = OrderedDict()
        self._item_explicit_sieves = OrderedDict()
        self._attribute_sieves = OrderedDict()
        self._computed_reference = None
        self._computed_projection = None

        self._setop = setop
        self._data = data # The data every sieve has to be referred

    def add_sieve(self, sieve, name=None):
        '''
        Every sieve has to share the same data otherwise a ValueError is
        raised

        :param sieve: A sieve could be either an ImplicitSieve or an
        ExplicitSieve.
        :param name: If not provided a uuid is generated
        :returns: sieve The added sieve
        '''
        name = name if name is not None else str(uuid.uuid4())
        if self.has_sieve(name):
            raise ValueError("Already exists a sieve with the name given")

        self._check_data(sieve.data)

        if isinstance(sieve, AttributeImplicitSieve):
            self._attribute_sieves[name] = sieve
            self._computed_projection = None
        elif isinstance(sieve, ItemImplicitSieve):
            self._item_implicit_sieves[name] = sieve
            self._computed_reference = None
        elif isinstance(sieve, ItemExplicitSieve):
            self._item_explicit_sieves[name] = sieve
            self._computed_reference = None

        return sieve

    def set_sieve(self, name, sieve):
        '''
        :param name: The key of the sieve.
        :param sieve: A sieve could be either an ImplicitSieve or an
        ExplicitSieve.
        :returns: sieve The setted sieve
        '''
        self._check_data(sieve.data)
        if isinstance(sieve, AttributeImplicitSieve):
            self._attribute_sieves[name] = sieve
            self._computed_projection = None
        elif isinstance(sieve, ItemImplicitSieve):
            self._item_implicit_sieves[name] = sieve
            self._computed_reference = None
        elif isinstance(sieve, ItemExplicitSieve):
            self._item_explicit_sieves[name] = sieve
            self._computed_reference = None
        return sieve

    def remove_sieve(self, name):
        '''
        :param name: The key of the sieve.
        '''
        if name in self._item_implicit_sieves:
            self._item_implicit_sieves.pop(name)
            self._computed_reference = None
        elif name in self._item_explicit_sieves:
            self._item_explicit_sieves.pop(name)
            self._computed_reference = None
        elif name in self._attribute_sieves:
            self._attribute_sieves.pop(name)
            self._computed_projection = None
        else:
            raise ValueError("There is no sieve with the name given")


    def has_sieve(self, name):
        '''
        :param name: The key of the sieve.
        '''
        return (name in self._item_implicit_sieves
                or name in self._item_explicit_sieves
                or name in self._attribute_sieves)

    def get_sieve(self, name):
        '''
        :param name: The key of the sieve.
        '''
        if name in self._item_implicit_sieves:
            return self._item_implicit_sieves[name]
        if name in self._item_explicit_sieves:
            return self._item_explicit_sieves[name]
        if name in self._attribute_sieves:
            return self._attribute_sieves[name]

    def is_empty(self):
        return (len(self._item_implicit_sieves) == 0
                and len(self._item_explicit_sieves) == 0
                and len(self._attribute_sieves) == 0)

    @property
    def reference(self):
        '''
        The reference resulting of the accumulation of every item sieve.  A
        reference is a set of indices or set([]) if there are no
        sieves
        '''
        if self._computed_reference is None:
            self._computed_reference = self._compute_reference()
        return self._computed_reference.items

    @property
    def projection(self):
        '''
        The projection resulting of the accumulation of every attribute
        sieve.  A projection is a dict of { 'attr_name' -> Bool } or
        {} if there are no sieves
        '''
        if self._computed_projection is None:
            self._computed_projection = self._compute_projection()
        return self._computed_projection.projection

    @property
    def query(self):
        '''
        The query resulting of the accumulation of every sieve.
        '''
        if self._computed_reference is None:
            self._computed_reference = self._compute_reference()
        return self._computed_reference.query

    def _check_data(self, data):
        if data != self._data:
            raise ValueError("Sieves in this SieveSet has {0} dataset not {1}"
                             .format(self._data.name, data.name))

    def _arggregate(self, a, b):
        if self._setop == 'AND':
            a.intersect(b)
        if self._setop == 'OR':
            a.union(b)

    def _compute_reference(self):
        explicit_sieves = self._item_explicit_sieves.values()
        implicit_sieves = self._item_implicit_sieves.values()
        aggregated_sieve = None

        if (len(self._item_implicit_sieves) == 0
            and len(self._item_explicit_sieves) == 0):
            return ItemImplicitSieve(self._data, [])

        explicit_sieve = None
        if len(explicit_sieves) > 0:
            explicit_sieve = copy(explicit_sieves[0])
            for c in explicit_sieves[1:]:
                self._arggregate(explicit_sieve, c.query)

        implicit_sieve = None
        if len(implicit_sieves) > 0:
            implicit_sieve = ItemImplicitSieve(self._data,
                implicit_sieves[0].items)
            for c in implicit_sieves[1:]:
                self._arggregate(implicit_sieve, c.items)

        if explicit_sieve and implicit_sieve:
            self._arggregate(explicit_sieve, implicit_sieve.query)
            aggregated_sieve = explicit_sieve
        elif explicit_sieve:
            aggregated_sieve = explicit_sieve
        elif implicit_sieve:
            aggregated_sieve = implicit_sieve

        return aggregated_sieve

    def _compute_projection(self):
        attribute_sieves = self._attribute_sieves.values()
        implicit_sieve = None
        if len(attribute_sieves) > 0:
            implicit_sieve = copy(attribute_sieves[0])
            for c in attribute_sieves[1:]:
                self._arggregate(implicit_sieve, c.index)
        else:
            implicit_sieve = AttributeImplicitSieve(self._data, [])


        return implicit_sieve
