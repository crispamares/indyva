# -*- coding: utf-8 -*-
'''
Created on 17/07/2013

:author: jmorales
'''

from indyva.external.tinyrpc.dispatch import RPCDispatcher
from .front_service import FrontService
from .session_service import SessionService
from .grava_service import GrammarService
from indyva.dataset import table_service, shared_object_service
from indyva.epubsub import hub_service
from indyva.dynamics import condition_service, dselect_service, dfilter_service
from indyva.IO import io_service
from indyva.core.context import SessionSingleton


class Front(RPCDispatcher, SessionSingleton):
    '''
    This class centralizes the access to the provided services
    '''

    def __init__(self):
        RPCDispatcher.__init__(self)

#        self.add_method(self.echo)
#        self.add_service(FrontService(self, 'FrontSrv'))
        self.add_service(table_service.TableService('TableSrv'))
        self.add_service(shared_object_service.SharedObjectService('SharedObjectSrv'))
        self.add_service(hub_service.HubService('HubSrv'))
        self.add_service(condition_service.ConditionService('ConditionSrv'))
        self.add_service(dselect_service.DynSelectService('DynSelectSrv', 'ConditionSrv'))
        self.add_service(dfilter_service.DynFilterService('DynFilterSrv', 'ConditionSrv'))
        self.add_service(io_service.IOService('IOSrv', 'TableSrv'))
        self.add_service(GrammarService('GrammarSrv'))


    def add_service(self, service):
        subdispatcher = RPCDispatcher()
        service.register_in(subdispatcher)
        self.add_subdispatch(subdispatcher, service.name + '.')

    def echo(self, a):
        return a



class ContextFreeFront(Front):
    '''
    This class centralizes the access to the provided services that
    not deppend on the current context.
    '''

    def __init__(self):
        RPCDispatcher.__init__(self)

        self.add_method(self.echo)
        self.add_service(FrontService(self, 'FrontSrv'))
        self.add_service(SessionService('SessionSrv'))

    def has_method(self, name):
        try:
            self.get_method(name)
        except KeyError:
            return False
        return True

    def echo(self, a):
        return a
