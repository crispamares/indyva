# -*- coding: utf-8 -*-
'''
Created on 03/07/2013

:author: jmorales
'''

from indyva.epubsub import pub_result
from .condition_set import ConditionSet
from .condition import CategoricalCondition, AttributeCondition, RangeCondition, QueryCondition
from indyva.core.grava import register


@register("filter")
class DynFilter(ConditionSet):
    '''
    This class maintain the state of the Filter Interactive Dynamic

    All references from each conditions are aggregated with Intersection set
    operation (a.k.a. AND) unless you specify the contrary
    '''

    def __init__(self, name, data, setop='AND', prefix=''):
        '''
        :param str name: unique name
        :param data: the dataset that is going to suffer the conditions
        :param str setop: [AND, OR] Is the aggregation operation for sets
        :param str prefix: Prepended to the name creates the oid
        '''
        ConditionSet.__init__(self, name, data, setop=setop, prefix=prefix)

    @property
    def grammar(self):
        grammar = ConditionSet.grammar.fget(self)
        grammar['type'] = 'filter'
        return grammar

    @pub_result('change')
    def new_categorical_condition(self, *args, **kwargs):
        '''
        :param str attr: The attribute that will be used as the category
        :param categories: The categories initially included
        :param str name: If a name is not provided, an uuid is generated
        :param int bins: If provided, the attribute will be coerced to be
        :param str prefix: Prepended to the name creates the oid
        :return: CategoricalCondition The created condition
        '''
        condition = CategoricalCondition(self._data, *args, **kwargs)
        self._add_condition(condition)
        return condition

    @pub_result('change')
    def new_attribute_condition(self, *args, **kwargs):
        '''
        :param attributes: The attributes initially included
        :param str name: If a name is not provided, an uuid is generated
        :param str prefix: Prepended to the name creates the oid
        :return: AttributeCondition The created condition
        '''
        condition = AttributeCondition(self._data, *args, **kwargs)
        self._add_condition(condition)
        return condition

    @pub_result('change')
    def new_range_condition(self, *args, **kwargs):
        '''
        :param attr: The attribute that will compared with range values.
        :param range: {min: val, max: val} The maximum and minimum values
            of the condition.
            All items whose attr value is inside the range are considered as
            included.
        :param domain: {min: val, max: val} The domain of the RangeCondition
            are the maximum and minimum values that the range can get.
        :param name: If a name is not provided, an uuid is generated
        :param str prefix: Prepended to the name creates the oid
        :return: RangeCondition The created condition
        '''
        condition = RangeCondition(self._data, *args, **kwargs)
        self._add_condition(condition)
        return condition


    @pub_result('change')
    def new_query_condition(self, *args, **kwargs):
        '''
        :param data: The dataset that will be queried
        :param query: A MongoDB query
        :param name: If a name is not provided, an uuid is generated
        :param str prefix: Prepended to the name creates the oid
        '''
        condition = QueryCondition(self._data, *args, **kwargs)
        self._add_condition(condition)
        return condition
