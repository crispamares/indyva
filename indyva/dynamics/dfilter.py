# -*- coding: utf-8 -*-
'''
Created on 03/07/2013

:author: jmorales
'''

from indyva.epubsub import pub_result
from .condition_set import ConditionSet
from .condition import CategoricalCondition, AttributeCondition

class DynFilter(ConditionSet):
    '''
    This class maintain the state of the Filter Interactive Dynamic
    
    All references from each conditions are aggregated with Intersection set 
    operation (a.k.a. AND) unless you specify the contrary
    '''

    def __init__(self, name, data, setop='AND'):
        '''
        :param str name: unique name
        :param data: the dataset that is going to suffer the conditions
        '''
        ConditionSet.__init__(self, name, data, namespace='f', setop=setop)

    @pub_result('change')
    def new_categorical_condition(self, *args, **kwargs):
        '''
        :param str attr: The attribute that will be used as the category
        :param categories: The categories initially included  
        :param str name: If a name is not provided, an uuid is generated
        :param int bins: If provided, the attribute will be coerced to be
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
        :return: AttributeCondition The created condition        
        '''
        condition = AttributeCondition(self._data, *args, **kwargs)
        self._add_condition(condition)
        return condition
        

