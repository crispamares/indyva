# -*- coding: utf-8 -*-
'''
Created on 10/08/2013

:author: jmorales
'''

from indyva.epubsub import IPublisher, pub_result, Bus
from indyva.core.names import INamed
from indyva.core.grava import IDefined
from .sieve import SieveSet
from .condition import Condition


class ConditionSet(IPublisher, INamed, IDefined):
    '''
    This class is a collection of conditions. Is used as the base class for
    DynFilter and DynSelect
    '''

    def __init__(self, name, data, setop='AND', prefix=''):
        '''
        :param str name: unique name
        :param data: the dataset that is going to suffer the conditions
        :param str setop: [AND, OR] Is the aggregation operation for sets
        :param str prefix: Prepended to the name creates the oid
        '''
        INamed.__init__(self, name, prefix=prefix)
        self._data = data
        self._setop = setop
        self._sieves = SieveSet(data, setop)

        self._conditions = {}

        topics = ['change', 'remove']
        bus = Bus(prefix='{0}{1}:'.format(prefix, self._name))
        IPublisher.__init__(self, bus, topics)

    def _retransmit_change(self, topic, msg):
        # print "retransmit"
        msg['original_topic'] = topic
        condition_oid = msg['origin']
        condition = self._conditions[condition_oid]
        if condition.enabled:
            self._sieves.set_sieve(condition_oid, condition.sieve)
        elif self._sieves.has_sieve(condition_oid):
            self._sieves.remove_sieve(condition_oid)
        self._bus.publish('change', msg)

    def _set_condition(self, condition):
        '''
        This method is the one that inserts conditions in the ConditionSet

        :param Condition condition: A Condition
        '''
        if condition.data != self._data:
            raise ValueError("Condition has {0} dataset, {1} expected"
                             .format(condition.data.name, self._data.name))
        self._conditions[condition.oid] = condition
        condition.subscribe('change', self._retransmit_change)
        condition.subscribe('enable', self._retransmit_change)
        if condition.enabled:
            self._sieves.set_sieve(condition.oid, condition.sieve)
        return condition

    @pub_result('change')
    def add_condition(self, condition):
        '''
        If the condition (oid) already exists a ValueError is raised.
        Every condition has to share the same data as this dynamic otherwise
         a ValueError is raised
        :param Condition condition: A Condition
        '''
        return self._add_condition(condition)

    def _add_condition(self, condition):
        '''
        If the condition (oid) already exists a ValueError is raised.
        Every condition has to share the same data as this dynamic otherwise
         a ValueError is raised
        :param Condition condition: A Condition
        '''
        if self.has_condition(condition.oid):
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
        if not self.has_condition(condition.oid):
            raise ValueError("There are no conditions with the given name: {0}"
                             .format(condition.name))
        return self._set_condition(condition)

    @pub_result('remove')
    def remove_condition(self, condition):
        '''
        :param condition: Could be a the oid of the condition itself
        '''
        oid = condition.oid if isinstance(condition, Condition) else condition
        self._conditions.pop(oid)
        self._sieves.remove_sieve(oid)
        return oid

    def has_condition(self, condition):
        '''
        :param condition: Could be a the oid of the condition itself
        '''

        oid = condition.oid if isinstance(condition, Condition) else condition
        return oid in self._conditions and self._sieves.has_sieve(oid)

    def get_condition(self, oid, default=None):
        '''
        :param str oid: The key of the condition.
        '''
        return self._conditions.get(oid, default)

    def get_conditions(self):
        '''
        :returns list: The list of conditions already in the `ConditionSet`
        '''
        return self._conditions.values()

    def clear(self):
        '''
        Remove all conditions in the condition set
        '''
        for oid in self._conditions.keys():
            self.remove_condition(oid)

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

    @property
    def grammar(self):
        conditions = [c.name for c in self._conditions.values()]

        return dict(name = self.name,
                    setop = self._setop,
                    data = self._data.name,
                    conditions = conditions)

    @classmethod
    def build(cls, grammar, objects):
        dataset = objects[grammar['data']]
        conditions = [objects[c] for c in grammar['conditions']]

        self = cls(name=grammar['name'],
                   data=dataset,
                   setop=grammar['setop'])

        for c in conditions:
            self.add_condition(c)

        return self


    @property
    def grammar_of_conditions(self):
        return [c.grammar for c in self._conditions.values()]


    def __repr__(self):
        return '{0}: {1} -> {2}'.format(type(self), self._name, self._conditions)
