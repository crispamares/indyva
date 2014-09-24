# -*- coding: utf-8 -*-
'''
Created on 05/12/2013

@author: jmorales
'''
from indyva.core.names import INamed
from .remote_service import RemoteService


class FrontService(INamed):
    '''
    This class provides facility services regarding the exposed services.

    Through this class remote clients can expose services to the rest of the
    system.

    Also online documentation of exposed modules can be requested through this
    service.
    '''

    def __init__(self, front, name='FrontSrv'):
        '''
        :param name: The unique name of the service
        '''
        self.front = front
        INamed.__init__(self, name)

    def expose(self, service_name, endpoint, srv_description):
        service = RemoteService(endpoint, srv_description, service_name)
        self.front.add_service(service)

    def register_in(self, dispatcher):
        dispatcher.add_method(self.expose)
