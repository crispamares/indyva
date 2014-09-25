# -*- coding: utf-8 -*-
'''
Created on 17/07/2013

:author: jmorales
'''

from contextlib import closing

from indyva.external.tinyrpc.dispatch import RPCDispatcher, ServerError
from indyva.core import Singleton
from indyva.core.context import Context
from .front import Front


class Dispatcher(RPCDispatcher, Singleton):
    '''
    This class centralizes the access to the provided services
    '''

    def __init__(self):
        RPCDispatcher.__init__(self)

        self._middlewares = []

    def instert_middleware(self, index, middleware):
        self._middlewares.insert(index, middleware)

    def _dispatch(self, request):
        try:
            _context = request.kwargs.pop('_context', None)
            _params = request.kwargs.pop('_params', None)
            if _params:
                request.args = _params
            with closing(Context.instance().open(_context)):
                for middleware in self._middlewares:
                    middleware.run(_context)
                print "----------------------------------->"
                response = Front.instance()._dispatch(request)
                print "<-----------------------------------"
            return response
        except Exception:
            # unexpected error, do not let client know what happened
            return request.error_respond(ServerError("Error processing the context:\n"
                                                     + str(_context)))
