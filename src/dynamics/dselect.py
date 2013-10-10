# -*- coding: utf-8 -*-
'''
Created on 03/07/2013

@author: jmorales
'''

from condition_set import ConditionSet
from dynamics.condition import CategoricalCondition
from epubsub import pub_result

class DynSelect(ConditionSet):
    '''
    This class maintain the state of the Select Interactive Dynamic
    
    All references from each conditions are aggregated with Union set operation
     (a.k.a. OR)
    '''

    def __init__(self, name, data):
        '''
        :param str name: unique name
        :param data: the dataset that is going to suffer the conditions
        '''
        ConditionSet.__init__(self, name, data, prefix='s')

    @pub_result('change')
    def new_categorical_condition(self, *args, **kwargs):
        '''
        :param str attr: The attribute that will be used as the category  
        :param str name: If a name is not provided, an uuid is generated
        :param int bins: If provided, the attribute will be coerced to be
        :return: CategoricalCondition The created condition
        '''
        condition = CategoricalCondition(self._data, *args, **kwargs)
        self._add_condition(condition)
        return condition
