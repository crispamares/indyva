# -*- coding: utf-8 -*-
'''
Created on 20/11/2013

@author: jmorales
'''

from functools import partial

from indyva.names import INamed
from indyva.facade.showcase import Showcase
from .condition import ( Condition, CategoricalCondition, AttributeCondition,
                         RangeCondition ) 


class ConditionService(INamed):
    '''
    This class provide a facade for managing Condition objects
    '''

    def __init__(self, name='ConditionSrv'):
        '''
        @param name: The unique name of the service
        '''
        self._conditions = Showcase.instance().get_case(name)
        INamed.__init__(self, name)
    
    def register_in(self, dispatcher):
        dispatcher.add_method(self.new_condition)
        dispatcher.add_method(self.expose_condition)
        dispatcher.add_method(self.del_condition)
        # Condition Properties
        dispatcher.add_method(partial(self._proxy_property, 'name'), 'name')
        dispatcher.add_method(partial(self._proxy_property, 'data'), 'data')
        dispatcher.add_method(partial(self._proxy_property, 'grammar'), 'grammar')
        # Condition Methods
        dispatcher.add_method(partial(self._proxy, 'include_all'), 'include_all')
        dispatcher.add_method(partial(self._proxy, 'exclude_all'), 'exclude_all')

        # CategoricalCondition Properties
        dispatcher.add_method(partial(self._proxy_property, 'attr'), 'attr')
        dispatcher.add_method(partial(self._proxy, 'get_condition'), 'get_condition')
        # CategoricalCondition Methods
        dispatcher.add_method(partial(self._proxy, 'included_categories'), 'included_categories')
        dispatcher.add_method(partial(self._proxy, 'excluded_categories'), 'excluded_categories')
        dispatcher.add_method(partial(self._proxy, 'included_items'), 'included_items')
        dispatcher.add_method(partial(self._proxy, 'excluded_items'), 'excluded_items')
        dispatcher.add_method(partial(self._proxy, 'add_category'), 'add_category')
        dispatcher.add_method(partial(self._proxy, 'remove_category'), 'remove_category')
        dispatcher.add_method(partial(self._proxy, 'toggle_category'), 'toggle_category')

        # AttributeCondition Methods
        dispatcher.add_method(partial(self._proxy, 'included_attributes'), 'included_attributes')
        dispatcher.add_method(partial(self._proxy, 'excluded_attributes'), 'excluded_attributes')
        dispatcher.add_method(partial(self._proxy, 'add_attribute'), 'add_attribute')
        dispatcher.add_method(partial(self._proxy, 'remove_attribute'), 'remove_attribute')
        dispatcher.add_method(partial(self._proxy, 'toggle_attribute'), 'toggle_attribute')

        #RangeCondition Properties
        dispatcher.add_method(partial(self._proxy_property, 'range'), 'range')
        dispatcher.add_method(partial(self._proxy_property, 'domain'), 'domain')
        # RangeCondition Methods
        dispatcher.add_method(partial(self._proxy, 'set_range'), 'set_range')

    def _proxy(self, method, condition_name, *args, **kwargs):
        condition = self._conditions[condition_name]
        result = condition.__getattribute__(method)(*args, **kwargs)
        if isinstance(result, Condition):
            self._conditions[result.full_name] = result
        return result
    
    def _proxy_property(self, method, condition_name):
        condition = self._conditions[condition_name]
        result = condition.__getattribute__(method)
        if isinstance(result, Condition):
            self._conditions[result.full_name] = result
        return result
            
    def new_condition(self, kind, data, *args, **kwargs):
        dataset = Showcase.instance().get(data)
        if kind == 'categorical':
            new_condition = CategoricalCondition(dataset, *args, **kwargs)
        if kind == 'attribute':
            new_condition = AttributeCondition(dataset, *args, **kwargs)
        if kind == 'range':
            new_condition = RangeCondition(dataset, *args, **kwargs)
        self._conditions[new_condition.full_name] = new_condition
        return new_condition

    def expose_condition(self, condition):
        self._conditions[condition.full_name] = condition
        return condition

    def del_condition(self, name):
        self._conditions.pop(name)