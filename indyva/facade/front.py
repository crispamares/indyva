# -*- coding: utf-8 -*-
'''
Created on 17/07/2013

@author: jmorales
'''

from indyva.external.tinyrpc.dispatch import RPCDispatcher
from .front_service import FrontService
from indyva.dataset import table_service, shared_object_service
from indyva.epubsub import hub_service
from indyva.dynamics import condition_service, dselect_service, dfilter_service
from indyva.IO import io_service


class Front(RPCDispatcher):
    '''
    This class centralizes the access to the provided services
    '''
    @staticmethod
    def instance():
        """Returns a global `Loop` instance.

        :warning: Not ThreadSafe.
        """
        if not hasattr(Front, "_instance"):
            Front._instance = Front()
        return Front._instance

    @staticmethod
    def initialized():
        """Returns true if the singleton instance has been created."""
        return hasattr(Front, "_instance")

    def install(self):
        """Installs this `Front` object as the singleton instance.

        This is normally not necessary as `instance()` will create
        an `Front` on demand, but you may want to call `install` to use
        a custom subclass of `Front`.
        """
        assert not Front.initialized()
        Front._instance = self

    def __init__(self):
        RPCDispatcher.__init__(self)

        self.add_method(self.echo)
        self.add_service(FrontService(self, 'FrontSrv'))
        self.add_service(table_service.TableService('TableSrv'))
        self.add_service(shared_object_service.SharedObjectService('SharedObjectSrv'))
        self.add_service(hub_service.HubService('HubSrv'))
        self.add_service(condition_service.ConditionService('ConditionSrv'))
        self.add_service(dselect_service.DynSelectService('DynSelectSrv', 'ConditionSrv'))
        self.add_service(dfilter_service.DynFilterService('DynFilterSrv', 'ConditionSrv'))
        self.add_service(io_service.IOService('IOSrv', 'TableSrv'))

    def add_service(self, service):
        subdispatcher = RPCDispatcher()
        service.register_in(subdispatcher)
        self.add_subdispatch(subdispatcher, service.name + '.')

    def echo(self, a):
        return a
