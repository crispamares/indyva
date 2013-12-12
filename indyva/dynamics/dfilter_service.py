# -*- coding: utf-8 -*-
'''
Created on 20/11/2013

@author: jmorales
'''
from indyva.facade.showcase import Case, Showcase
from indyva.names import INamed
from .dfilter import DynFilter


class DynFilterService(INamed):
    '''
    This class provide a facade for managing DynFilter objects
    '''

    def __init__(self, name='DynFilterSrv'):
        '''
        @param name: The unique name of the service
        '''
        self._dfilters = Case()
        INamed.__init__(self, name)
    
    def register_in(self, dispatcher):
        dispatcher.add_method(self.new_dfilter)
        dispatcher.add_method(self.expose_dfilter)
        dispatcher.add_method(self.del_dfilter)
        
    def new_dfilter(self, name, data):
        dataset = Showcase.instance().get(data)
        new_dfilter = DynFilter(name, dataset)
        self._dfilters[new_dfilter.full_name] = new_dfilter
        return new_dfilter

    def expose_dfilter(self, dfilter):
        self._dfilters[dfilter.full_name] = dfilter
        return dfilter

    def del_dfilter(self, name):
        self._dfilters.pop(name)