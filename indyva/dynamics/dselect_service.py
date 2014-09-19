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
        dispatcher.add_method(self.clear)
        # DynSelect Methods
        dispatcher.add_method(partial(self._proxy, 'new_categorical_condition'), 'new_categorical_condition')
        dispatcher.add_method(partial(self._proxy, 'new_range_condition'), 'new_range_condition')
        dispatcher.add_method(partial(self._proxy, 'new_query_condition'), 'new_query_condition')
        # ConditionSet Methods
        dispatcher.add_method(partial(self._proxy, 'add_condition'), 'add_condition')
        dispatcher.add_method(partial(self._proxy, 'set_condition'), 'set_condition')
        dispatcher.add_method(partial(self._proxy, 'update'), 'update')
        dispatcher.add_method(partial(self._proxy, 'remove_condition'), 'remove_condition')
        dispatcher.add_method(partial(self._proxy, 'has_condition'), 'has_condition')
        dispatcher.add_method(partial(self._proxy, 'get_condition'), 'get_condition')
        # ConditionSet Properties
        dispatcher.add_method(partial(self._proxy_property, 'name'), 'name')
        dispatcher.add_method(partial(self._proxy_property, 'grammar'), 'grammar')
        dispatcher.add_method(partial(self._proxy_property, 'reference'), 'reference')
        dispatcher.add_method(partial(self._proxy_property, 'projection'), 'projection')
        dispatcher.add_method(partial(self._proxy_property, 'query'), 'query')
        dispatcher.add_method(partial(self._proxy_property, 'view_args'), 'view_args')

    def _proxy(self, method, dselect_oid, *args, **kwargs):
        dselect = self._dselects[dselect_oid]
        result = dselect.__getattribute__(method)(*args, **kwargs)
        if isinstance(result, Condition):
            self._conditions[result.oid] = result
        return result

    def _proxy_property(self, method, dselect_oid):
        dselect = self._dselects[dselect_oid]
        result = dselect.__getattribute__(method)
        if isinstance(result, Condition):
            self._conditions[result.oid] = result
        return result

    def new_dselect(self, name, data, setop='OR', prefix=''):
        dataset = Showcase.instance().get(data)
        new_dselect = DynSelect(name, dataset, setop, prefix=prefix)
        self._dselects[new_dselect.oid] = new_dselect
        return new_dselect

    def expose_dselect(self, dselect):
        self._dselects[dselect.oid] = dselect
        return dselect

    def del_dselect(self, oid):
        self._dselects.pop(oid)

    def clear(self):
        self._dselects.clear()
        self._conditions.clear()
