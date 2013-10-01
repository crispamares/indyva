# -*- coding: utf-8 -*-
'''
Created on 10/07/2013

@author: jmorales
'''
from collections import OrderedDict
import uuid
from copy import copy


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
        return str(self.index)



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
        return { column : (column in self.index) for column in self.domain}
        
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

    def to_implicit(self):
        if self._implicit_form is None:
            domain = self._data.index_domain()
            index = self._data.find(self._query).index_domain()
            self._implicit_form = ImplicitSieve(domain, index)
        return self._implicit_form
    
    def __eq__(self, other):
        return self.data is other.data and self.query == other.query
    
    def __repr__(self):
        return str(self.query)


class SieveSet(object):
    def __init__(self, setop='AND'):
        '''@param setop: The set operation. AND or OR'''
        self._item_conditions = OrderedDict()
        self._attribute_conditions = OrderedDict()
        self._computed_reference = None
        self._computed_projection = None

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

        if isinstance(condition, AttributeImplicitSieve):
            self._attribute_conditions[name] = condition
        elif isinstance(condition, (ItemImplicitSieve, ItemExplicitSieve)):
            self._item_conditions[name] = condition
        self._dirty()

    def set_condition(self, name, condition):
        ''' 
        @param name: The key of the condition. 
        @param condition: A condition could be either an ImplicitSieve or an 
        ExplicitSieve. 
        '''
        if isinstance(condition, AttributeImplicitSieve):
            self._attribute_conditions[name] = condition
        elif isinstance(condition, (ItemImplicitSieve, ItemExplicitSieve)):
            self._item_conditions[name] = condition
        self._dirty()   
    
    def remove_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        if name in self._item_conditions:
            self._item_conditions.pop(name)
        if name in self._attribute_conditions:
            self._attribute_conditions.pop(name)
        else:
            raise ValueError("There is no condition with the name given")
        self._dirty()

    def has_condition(self, name):
        ''' 
        @param name: The key of the condition. 
        '''
        return name in self._item_conditions or name in self._attribute_conditions
    
    def is_empty(self):
        return len(self._item_conditions) == 0 and len(self._attribute_conditions)    

    @property
    def ref(self):
        '''The reference resulting of the accumulation of every item condition.
        A reference is a set of indices or set([]) if there are no conditions'''
        if self._computed_reference is None:
            self._computed_reference = self._compute_reference()
        return self._computed_reference
    
    @property
    def projection(self):
        '''The projection resulting of the accumulation of every attribute 
        condition.
        A projection is a dict of { 'attr_name' -> Bool } or {} if there are 
        no conditions
        '''
        if self._computed_projection is None:
            self._computed_projection = self._compute_projection()
        return self._computed_projection

    @property
    def query(self):
        '''The query resulting of the accumulation of every condition.
        @param index: A string or list of strings'''
        if len(self._item_conditions) == 0:
            return {}
        if self._computed_reference is None:
            self._computed_reference = self._compute_reference()

        return self._computed_reference.query
        
    def _dirty(self):
        self._computed_reference = None
        self._computed_projection = None
        
    def _compute_reference(self):
        conditions = [c for c in self._item_conditions.values()]
        reference = copy(conditions[0])
        for c in conditions[1:]:
            if self.setop == 'AND':
                reference.intersect(c)
            if self.setop == 'OR':
                reference.union(c)
        return reference


















































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
        print self._conditions.values()
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

