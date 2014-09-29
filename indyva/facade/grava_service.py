# -*- coding: utf-8 -*-
'''

:author: jmorales
'''
from indyva.core.names import INamed
from indyva.core.context import Context, Session


class GrammarService(INamed):
    '''
    This class let clients to get the grammar describing.
    '''

    def __init__(self, name='GrammarSrv'):
        '''
        :param name: The unique name of the service
        '''
        INamed.__init__(self, name)


    def register_in(self, dispatcher):
        # dispatcher.add_method(self.open_session)
