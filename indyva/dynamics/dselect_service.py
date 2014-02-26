# -*- coding: utf-8 -*-
'''
Created on 20/11/2013

@author: jmorales
'''

from functools import partial

from indyva.names import INamed
from indyva.facade.showcase import Showcase
from .dselect import DynSelect
from .condition import Condition


class DynSelectService(INamed):
    '''
    This class provide a facade for managing DynSelect objects
    '''

    def __init__(self, name='DynSelectSrv', condition_srv_name='ConditionSrv'):
        '''
        @param name: The unique name of the service
        '''
        self._dselects = Showcase.instance().get_case(name)
        self._conditions = Showcase.instance().get_case(condition_srv_name)
        INamed.__init__(self, name)
    
    def register_in(self, dispatcher):
        dispatcher.add_method(self.new_dselect)
        dispatcher.add_method(self.expose_dselect)
        dispatcher.add_method(self.del_dselect)
        # DynSelect Methods
        dispatcher.add_method(partial(self._proxy, 'new_categorical_condition'), 'new_categorical_condition')
        dispatcher.add_method(partial(self._proxy, 'new_range_condition'), 'new_range_condition')
        # ConditionSet Methods
        dispatcher.add_method(partial(self._condition_proxy, 'add_condition'), 'add_condition')
        dispatcher.add_method(partial(self._condition_proxy, 'set_condition'), 'set_condition')
        dispatcher.add_method(partial(self._condition_proxy, 'update'), 'update')
        dispatcher.add_method(partial(self._condition_proxy, 'remove_condition'), 'remove_condition')
        dispatcher.add_method(partial(self._condition_proxy, 'has_condition'), 'has_condition')
        dispatcher.add_method(partial(self._proxy, 'get_condition'), 'get_condition')
        # ConditionSet Properties
        dispatcher.add_method(partial(self._proxy_property, 'name'), 'name')
        dispatcher.add_method(partial(self._proxy_property, 'grammar'), 'grammar')
        dispatcher.add_method(partial(self._proxy_property, 'reference'), 'reference')
        dispatcher.add_method(partial(self._proxy_property, 'projection'), 'projection')
        dispatcher.add_method(partial(self._proxy_property, 'query'), 'query')
        dispatcher.add_method(partial(self._proxy_property, 'view_args'), 'view_args')

    def _proxy(self, method, dselect_name, *args, **kwargs):
        dselect = self._dselects[dselect_name]
        result = dselect.__getattribute__(method)(*args, **kwargs)
        if isinstance(result, Condition):
            self._conditions[result.full_name] = result
        return result
    
    def _proxy_property(self, method, dselect_name):
        dselect = self._dselects[dselect_name]
        result = dselect.__getattribute__(method)
        if isinstance(result, Condition):
            self._conditions[result.full_name] = result
        return result
    
    def _condition_proxy(self, method, dselect_name, condition):
        return self._proxy(method, dselect_name, Showcase.instance().get(condition))
        
    def new_dselect(self, name, data, setop='OR'):
        dataset = Showcase.instance().get(data)
        new_dselect = DynSelect(name, dataset, setop)
        self._dselects[new_dselect.full_name] = new_dselect
        return new_dselect

    def expose_dselect(self, dselect):
        self._dselects[dselect.full_name] = dselect
        return dselect

    def del_dselect(self, name):
        self._dselects.pop(name)
