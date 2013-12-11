# -*- coding: utf-8 -*-
'''
Created on 10/08/2013

:author: jmorales
'''

from epubsub import IPublisher, pub_result, Bus

from sieve import SieveSet
from dynamics.condition import Condition
from names import INamed

class ConditionSet(IPublisher, INamed):
    '''
    This class is a collection of conditions. Is used as the base class for
    DynFilter and DynSelect
    '''

    def __init__(self, name, data, namespace='cs', setop='AND'):
        '''
        :param str name: unique name
        :param data: the dataset that is going to suffer the conditions
        '''
        INamed.__init__(self, name, prefix=namespace+':')
        self._data = data
        self._sieves = SieveSet(data, setop)
        
        self._conditions = {}

        topics = ['change', 'remove']
        bus = Bus(prefix= '{0}:{1}:'.format(namespace, self._name))
        IPublisher.__init__(self, bus, topics)

    def _retransmit(self, topic, msg):
        #print "retransmit"
        msg['original_topic'] = topic
        condition_name = msg['origin']
        self._sieves.set_sieve(condition_name, self._conditions[condition_name].sieve)
        self._bus.publish('change', msg)

    def _set_condition(self, condition):
        '''
        This method is the one that inserts conditions in the ConditionSet
        
        :param Condition condition: A Condition
        '''
        if condition.data != self._data:
            raise ValueError("Condition has {0} dataset, {1} expected"
                             .format(condition.data.name, self._data.name))
        self._conditions[condition.name] = condition
        condition.subscribe('change', self._retransmit)
        self._sieves.set_sieve(condition.name, condition.sieve)
        return condition

    @pub_result('change')
    def add_condition(self, condition):
        '''
        If the condition (name) already exists a ValueError is raised.
        Every condition has to share the same data as this dynamic otherwise
         a ValueError is raised
        :param Condition condition: A Condition
        '''
        return self._add_condition(condition)

    def _add_condition(self, condition):
        '''
        If the condition (name) already exists a ValueError is raised.
        Every condition has to share the same data as this dynamic otherwise
         a ValueError is raised
        :param Condition condition: A Condition
        '''
        if self.has_condition(condition.name):
            raise ValueError(
                "Already exists a condition with the given name: {0}"
                .format(condition.name))
        return self._set_condition(condition)

    @pub_result('change')
    def set_condition(self, condition):
        '''
        Every condition has to share the same data as this dynamic otherwise
         a ValueError is raised
        
        :param Condition condition: A Condition
        '''
        return self._set_condition(condition)

    @pub_result('change')
    def update(self, condition):
        '''
        :param Condition condition: A previously added Condition
        '''
        if not self.has_condition(condition.name):
            raise ValueError("There are no conditions with the given name: {0}"
                             .format(condition.name))
        return self._set_condition(condition)
        
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
    
    def get_condition(self, name, default=None):
        ''' 
        :param str name: The key of the condition. 
        '''
        return self._conditions.get(name, default)
    
    def is_empty(self):
        return (not self._conditions) and self._sieves.is_empty() 
    
    @property
    def reference(self):
        '''The reference resulting of the accumulation of every item condition.
        A reference is a set of indices or None if there are no item conditions
        '''
        return list(self._sieves.reference)

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
    
    def __repr__(self):
        return '{0}: {1} -> {2}'.format(type(self), self._name, self._conditions)



            