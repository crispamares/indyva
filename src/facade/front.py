# -*- coding: utf-8 -*-
'''
Created on 17/07/2013

@author: jmorales
'''
from external.tinyrpc.dispatch import RPCDispatcher, public
from dataset import table_service

class Front(RPCDispatcher):
    '''
    This class centralizes the access to the provided services
    
    '''
    def __init__(self):
        RPCDispatcher.__init__(self)
        
        self.add_method(self.echo)
        self.add_service(table_service.TableService('TableSrv'))
        
    def add_service(self, service):
        subdispatcher = RPCDispatcher()
        service.register_in(subdispatcher)
        self.add_subdispatch(subdispatcher, service.name+'.')
        
    def echo(self, a):
        return a
