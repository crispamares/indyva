# -*- coding: utf-8 -*-
'''
Created on 10/07/2013

@author: jmorales
'''
from collections import OrderedDict
import uuid

class ImplicitSieve(object):

    def __init__(self, data, index=None):
        self._data = data
        self._domain = None
        self._index = index if index is not None else set()
    
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
    
    @property
    def query(self):
        raise NotImplemented()

    def union(self, index):
        self._index = self.index.union(set(index))

    def substract(self, index):
        self._index = self.index - set(index)
        
    def toggle(self):
        self._index = self.domain - self.index 

    def intersect(self, index):
        self._index.intersection_update(set(index))
    
    def to_explicit(self):
        raise NotImplemented()
    
    def __eq__(self, other):
        return self.domain == other.domain and self._index == other.index
    
    def __repr__(self):
        return 'Sieve: ' + str(self.index)



class ItemImplicitSieve(ImplicitSieve):

    @property
    def domain(self):
        if self._domain is None:
            self._domain = set(self.data.index_domain())
        return self._domain
    @property
    def query(self):
        return { self.data.index : {'$in': list(self._index)} }

    def to_explicit(self):
        query = { self.data.index : {'$in': list(self._index)} }
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
    def __init__(self, data, query=None):
        self._data = data
        self._domain = None
        self._query = query if query is not None else {}
        self._implicit_form = None
    
    @property
    def data(self):
        return self._data
    @property
    def domain(self):
        if self._domain is None:
            self._domain = set(self.data.index_domain())
        return self._domain
    @property
    def query(self):
        return self._query
    @query.setter
    def query(self, query):
        self._query = query
        self._implicit_form = None
    @property
    def index(self):
        self.to_implicit()
        return self._implicit_form.index

    def union(self, query):
        self.query = {'$or': [self._query, query]}

    def substract(self, query):
        self.query = {'$and': [self._query, {"$nor": [query]}]}

    def toggle(self):
        self.query = {'$nor': [self._query]}

    def intersect(self, query):
        self.query = {'$and': [self._query, query]}


    def to_implicit(self):
        if self._implicit_form is None:
            domain = self._data.index_domain()
            index = self._data.find(self._query).index_domain()
            self._implicit_form = ImplicitSieve(domain, index)
        return self._implicit_form
    
    def __eq__(self, other):
        return self.data is other.data and self.query == other.query
    
    def __repr__(self):
        return 'Sieve: ' + str(self.query)


def create_item_sieve(data, reference=None, query=None, *args):
    '''
    Both reference and query must not be provided at the same time
    
    @param data: DataSet of the sieve
    @param reference: A list of item keys
    @param query: An explicit query
    '''
    if reference is None and query is not None:
        raise ValueError('Both reference and query params provided')
    if reference is not None:
        sieve = ItemImplicitSieve(data, reference)
    if query is not None:
        sieve = ItemExplicitSieve(data, query)
    return sieve

class SieveSet(object):
    def __init__(self, setop='AND'):
        '''@param setop: The set operation. AND or OR'''
        self._item_implicit_conditions = OrderedDict()
        self._item_explicit_conditions = OrderedDict()
        self._attribute_conditions = OrderedDict()
        self._computed_reference = None
        self._computed_projection = None
        
        self._setop = setop
        self._data = None # The data every sieve has to be referred

    def add_condition(self, condition, name=None):
        ''' 
        Every condition has to share the same data otherwise a ValueError is
        raised
         
        @param condition: A condition could be either an ImplicitSieve or an 
        ExplicitSieve.  
        @param name: If not provided a uuid is generated 
        '''
        name = name if name is None else str(uuid.uuid4())
        if self.has_condition(name):
            raise ValueError("Already exists a condition with the name given")

        self._check_data(condition.data)

        if isinstance(condition, AttributeImplicitSieve):
            self._attribute_conditions[name] = condition
        elif isinstance(condition, ItemImplicitSieve):
            self._item_implicit_conditions[name] = condition
        elif isinstance(condition, ItemExplicitSieve):
            self._item_explicit_conditions[name] = condition
        self._dirty()

    def set_condition(self, name, condition):
        ''' 
        @param name: The key of the condition. 
        @param condition: A condition could be either an ImplicitSieve or an 
        ExplicitSieve. 
        '''
        self._check_data(condition.data)
        print condition
        if isinstance(condition, AttributeImplicitSieve):
            self._attribute_conditions[name] = condition
        elif isinstance(condition, ItemImplicitSieve):
            self._item_implicit_conditions[name] = condition
        elif isinstance(condition, ItemExplicitSieve):
            self._item_explicit_conditions[name] = condition
        self._dirty()   
    
    def remove_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        if name in self._item_implicit_conditions:
            self._item_implicit_conditions.pop(name)
        elif name in self._item_explicit_conditions:
            self._item_explicit_conditions.pop(name)
        elif name in self._attribute_conditions:
            self._attribute_conditions.pop(name)
        else:
            raise ValueError("There is no condition with the name given")
        self._dirty()

    def has_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        return (name in self._item_implicit_conditions
                or name in self._item_explicit_conditions
                or name in self._attribute_conditions)
    
    def is_empty(self):
        return (len(self._item_implicit_conditions) == 0 
                and len(self._item_explicit_conditions) == 0 
                and len(self._attribute_conditions) == 0)    

    @property
    def reference(self):
        '''The reference resulting of the accumulation of every item condition.
        A reference is a set of indices or set([]) if there are no conditions'''
        if self._computed_reference is None:
            self._computed_reference = self._compute_reference()
        return self._computed_reference.index
    
    @property
    def projection(self):
        '''The projection resulting of the accumulation of every attribute 
        condition.
        A projection is a dict of { 'attr_name' -> Bool } or {} if there are 
        no conditions
        '''
        if self._computed_projection is None:
            self._computed_projection = self._compute_projection()
        return self._computed_projection.projection

    @property
    def query(self):
        '''The query resulting of the accumulation of every condition.
        @param index: A string or list of strings'''
        if (len(self._item_implicit_conditions) == 0
            and len(self._item_explicit_conditions) == 0):
            return {}
        if self._computed_reference is None:
            self._computed_reference = self._compute_reference()

        return self._computed_reference.query
        
    def _check_data(self, data):
        if self._data is None:
            self._data = data
        elif data != self._data:
            raise ValueError("Sieves in this SieveSet has {0} dataset not {1}"
                             .format(self._data.name, data.name))


        
    def _dirty(self):
        self._computed_reference = None
        self._computed_projection = None
        
    def _arggregate(self, a, b):
        if self._setop == 'AND':
            a.intersect(b)
        if self._setop == 'OR':
            a.union(b)


    def _compute_reference(self):
        explicit_conditions = self._item_explicit_conditions.values()
        implicit_conditions = self._item_implicit_conditions.values()
        aggregated_sieve = None
         
        explicit_sieve = None
        if len(explicit_conditions) > 0:
            explicit_sieve = explicit_conditions[0]
            for c in explicit_conditions[1:]:
                self._arggregate(explicit_sieve, c.query)

        implicit_sieve = None
        if len(implicit_conditions) > 0:
            implicit_sieve = implicit_conditions[0]
            for c in implicit_conditions[1:]:
                self._arggregate(implicit_sieve, c.index)
        
        if explicit_sieve and implicit_sieve:        
            self._arggregate(explicit_sieve, implicit_sieve.query)
            aggregated_sieve = explicit_sieve
        elif explicit_sieve:
            aggregated_sieve = explicit_sieve
        elif implicit_sieve:
            aggregated_sieve = implicit_sieve

        return aggregated_sieve

    def _compute_projection(self):
        attribute_conditions = self._attribute_conditions.values()
        implicit_sieve = None
        if len(attribute_conditions) > 0:
            implicit_sieve = attribute_conditions[0]
            for c in attribute_conditions[1:]:
                self._arggregate(implicit_sieve, c.index)
        else:
            implicit_sieve = AttributeImplicitSieve(self._data)

                        
        return implicit_sieve
















































class ItemSieve(object):
    def __init__(self, setop='AND'):
        '''@param setop: The set operation. AND or OR'''
        self._conditions = OrderedDict()
        self._computed_reference = None
        self.setop = setop
        
    def add_condition(self, reference, query = None, name=None):
        ''' 
        @param reference: Reference is mandatory
        @param query: If the condition is explicit then a query is needed.
          Providing an explicit condition is useful for recomputing the 
          reference if the dataset changes 
        @param name: If not provided a uuid is generated 
        '''
        name = name if name is None else str(uuid.uuid4())
        if self._conditions.has_key(name):
            raise ValueError("Already exists a condition with the name given")
        self._conditions[name] = dict(reference=set(reference), query=query)
        self._dirty()

    def set_condition(self, name, reference, query=None):
        ''' 
        @param name: The key of the condition. 
        @param reference: Reference is mandatory
        @param query: If the condition is explicit then a query is needed.
          Providing an explicit condition is useful for recomputing the 
          reference if the dataset changes 
        '''
        self._conditions[name] = dict(reference=set(reference), query=query)
        self._dirty()   
    
    def remove_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        if not self._conditions.has_key(name):
            raise ValueError("There is no condition with the name given")
        del self._conditions[name]
        self._dirty()

    def has_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        return self._conditions.has_key(name) 
    
    def is_empty(self):
        return len(self._conditions) == 0    

    @property
    def ref(self):
        '''The reference resulting of the accumulation of every condition.
        A reference is a set of indices or None if there are no conditions'''
        if self._computed_reference is None:
            self._computed_reference = self._compute_reference()
        return self._computed_reference

    def query(self, index):
        '''The query resulting of the accumulation of every condition.
        @param index: A string or list of strings'''
        if self.is_empty():
            return {}
        if self._computed_reference is None:
            self._computed_reference = self._compute_reference()
        if isinstance(index, list):
            NotImplementedError('Multi Index is not supported yet')
        return { index : {'$in': list(self._computed_reference)} }
        
    def _dirty(self):
        self._computed_reference = None
        
    def _compute_reference(self):
        references = [v['reference'] for v in self._conditions.values()]
        
        if self.setop == 'AND':
            reference = set.intersection(*references)
        if self.setop == 'OR':
            reference = set.union(*references)
        return reference




class AttrSieve(object):
    def __init__(self):
        self._conditions = OrderedDict()
        self._computed_projection = None

    def add_condition(self, projection, name=None):
        ''' 
        @param projection: Projection is mandatory
        @param name: If not provided a uuid is generated 
        '''
        name = name if name is None else str(uuid.uuid4())
        if self._conditions.has_key(name):
            raise ValueError("Already exists a condition with the given name")
        self._conditions[name] = projection
        self._dirty()

    def set_condition(self, name, projection):
        ''' 
        @param name: The key of the condition. 
        @param projection: Projection is mandatory
        '''
        self._conditions[name] = projection
        self._dirty()   
    
    def remove_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        if self._conditions.has_key(name):
            raise ValueError("There is no condition with the given name")
        del self._conditions[name]
        self._dirty()

    def has_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        return self._conditions.has_key(name) 

    def is_empty(self):
        return len(self._conditions) == 0    

    @property
    def projection(self):
        '''The projection resulting of the accumulation of every condition.
        A projection is a dict of { 'attr_name' -> Bool } or None if there are no conditions'''
        if self._computed_projection is None:
            self._computed_projection = self._compute_projection()
        return self._computed_projection
        
    def _dirty(self):
        self._computed_projection = None
        
    def _compute_projection(self):
        if self.is_empty():
            return None
        projection = {}
        for p in self._conditions.values():
            projection.update( p )
        return projection

