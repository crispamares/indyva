# -*- coding: utf-8 -*-
'''
Created on 03/07/2013

:author: jmorales
'''

from epubsub.abc_publisher import IPublisher, pub_result
from epubsub.bus import Bus

from sieve import SieveSet
from dynamics.condition import CategoricalCondition, AttributeCondition,\
    Condition

class DynFilter(IPublisher):
    '''
    This class maintain the state of the Filter Interactive Dynamic
    
    All references from each conditions are aggregated with Intersection set 
    operation (a.k.a. AND)
    '''

    def __init__(self, name, data):
        '''
        :param str name: unique name
        :param data: the dataset that is going to suffer the conditions
        '''
        self._name = name
        self._data = data
        self._sieves = SieveSet(data)
        
        self._conditions = {}

        topics = ['change', 'remove']
        bus = Bus(prefix= 'f.'+self._name+'.')
        IPublisher.__init__(self, bus, topics)

    def new_categorical_condition(self, *args, **kwargs):
        '''
        :param str attr: The attribute that will be used as the category  
        :param str name: If a name is not provided, an uuid is generated
        :param int bins: If provided, the attribute will be coerced to be
        :return: CategoricalCondition The created condition
        '''
        condition = CategoricalCondition(self._data, *args, **kwargs)
        self.add_condition(condition)
        return condition
    
    def new_attribute_condition(self, *args, **kwargs):
        ''' 
        :param str name: If a name is not provided, an uuid is generated
        :return: AttributeCondition The created condition        
        '''
        condition = AttributeCondition(self._data, *args, **kwargs)
        self.add_condition(condition)
        return condition
        

    def add_condition(self, condition):
        '''
        If the condition (name) already exists a ValueError is raised.
        Every condition has to share the same data as this dynamic otherwise
         a ValueError is raised
        :param Condition condition: A Condition
        '''
        if self.has_condition(condition.name):
            raise ValueError("Already exists a condition with the given name")
        return self.set_condition(condition)

    @pub_result('change')
    def set_condition(self, condition):
        '''
        Every condition has to share the same data as this dynamic otherwise
         a ValueError is raised
        
        :param Condition condition: A Condition
        '''
        if condition.data != self._data:
            raise ValueError("Condition has {0} dataset, {1} expected"
                             .format(condition.data.name, self._data.name))
        self._conditions[condition.name] = condition
        self._sieves.set_sieve(condition.name, condition.sieve)
        return condition.name

 
    def update(self, condition):
        '''
        :param Condition condition: A previously added Condition
        '''
        if not self.has_condition(condition.name):
            raise ValueError("There are no conditions with the given name: {0}"
                             .format(condition.name))
        self.set_condition(condition)
        
    @pub_result('remove')
    def remove_condition(self, condition):
        ''' 
        :param condition: Could be a the name of the condition itself
        '''
        name = condition.name if isinstance(condition, Condition) else condition
        self._conditions.pop(name)
        self._sieves.remove_sieve(name)
        return name

    def has_condition(self, condition):
        ''' 
        :param condition: Could be a the name of the condition itself
        '''
        
        name = condition.name if isinstance(condition, Condition) else condition
        return name in self._conditions and self._sieves.has_sieve(name) 
    
    def get_condition(self, name):
        ''' 
        :param str name: The key of the condition. 
        '''
        return self._conditions.get_condition(name)
    
    def is_empty(self):
        return (not self._conditions) and self._sieves.is_empty() 
    
    @property
    def reference(self):
        '''The reference resulting of the accumulation of every item condition.
        A reference is a set of indices or None if there are no item conditions
        '''
        return self._sieves.reference

    @property
    def projection(self):
        '''The projection resulting of the accumulation of every attribute 
        condition.
        A projection is a dict of { 'attr_name' -> Bool } or None if there are 
        no conditions'''
        return self._sieves.projection
    
    @property
    def query(self):
        '''The query resulting of the accumulation of item conditions.
        '''
        return self._sieves.query
    
    @property
    def view_args(self):
        '''The view_args, that groups the query and the projection 
        :return: dict(query=>query, projection=>projection)
        '''
        return dict(query = self.query, projection= self.projection) 
    


            
