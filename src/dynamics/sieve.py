# -*- coding: utf-8 -*-
'''
Created on 10/07/2013

@author: jmorales
'''
from collections import OrderedDict
import uuid


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

