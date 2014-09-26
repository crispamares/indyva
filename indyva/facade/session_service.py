# -*- coding: utf-8 -*-
'''

:author: jmorales
'''
from indyva.core.names import INamed
from indyva.core.context import Context, Session


class SessionService(INamed):
    '''
    This class let clients to manage session opening and closing

    '''

    def __init__(self, name='SessionSrv'):
        '''
        :param name: The unique name of the service
        '''
        INamed.__init__(self, name)

    def open_session(self, name):
        session = Session(name)
        Context.instance().add_session(session, True)

    def close_session(self, name):
        Context.instance().remove_session(name)

    def use_session(self, name):
        context = Context.instance()
        if context.has_session(name):
            is_new = False
        else:
            session = Session(name)
            context.add_session(session)
            is_new = True
        return is_new

    def register_in(self, dispatcher):
        dispatcher.add_method(self.open_session)
        dispatcher.add_method(self.close_session)
        dispatcher.add_method(self.use_session)
