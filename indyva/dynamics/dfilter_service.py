# -*- coding: utf-8 -*-
'''
Created on 20/11/2013

@author: jmorales
'''


from functools import partial

from indyva.facade.showcase import Showcase
from indyva.names import INamed
from .dfilter import DynFilter
from .condition import Condition

class DynFilterService(INamed):
    '''
    This class provide a facade for managing DynFilter objects
    '''

    def __init__(self, name='DynFilterSrv', condition_srv_name='ConditionSrv'):
        '''
        @param name: The unique name of the service
        '''
        self._dfilters = Showcase.instance().get_case(name)
        self._conditions = Showcase.instance().get_case(condition_srv_name)
        INamed.__init__(self, name)

    def register_in(self, dispatcher):
        dispatcher.add_method(self.new_dfilter)
        dispatcher.add_method(self.expose_dfilter)
        dispatcher.add_method(self.del_dfilter)
        dispatcher.add_method(self.clear)
        # DynFilter Methods
        dispatcher.add_method(partial(self._proxy, 'new_categorical_condition'), 'new_categorical_condition')
        dispatcher.add_method(partial(self._proxy, 'new_attribute_condition'), 'new_attribute_condition')
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

    def _proxy(self, method, dfilter_oid, *args, **kwargs):
        dfilter = self._dfilters[dfilter_oid]
        result = dfilter.__getattribute__(method)(*args, **kwargs)
        if isinstance(result, Condition):
            self._conditions[result.oid] = result
        return result
    
    def _proxy_property(self, method, dfilter_oid):
        dfilter = self._dfilters[dfilter_oid]
        result = dfilter.__getattribute__(method)
        if isinstance(result, Condition):
            self._conditions[result.oid] = result
        return result
    
    def _condition_proxy(self, method, dfilter_oid, condition):
        return self._proxy(method, dfilter_oid,  self._conditions[condition])

    def new_dfilter(self, name, data, setop='AND'):
        dataset = Showcase.instance().get(data)
        new_dfilter = DynFilter(name, dataset, setop)
        self._dfilters[new_dfilter.oid] = new_dfilter
        return new_dfilter

    def expose_dfilter(self, dfilter):
        self._dfilters[dfilter.oid] = dfilter
        return dfilter

    def del_dfilter(self, oid):
        self._dfilters.pop(oid)

    def clear(self):
        self._dfilters.clear()
        self._conditions.clear()
