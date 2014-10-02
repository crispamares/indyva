# -*- coding: utf-8 -*-
'''
Created on 17/07/2013

:author: jmorales
'''

from contextlib import closing

from indyva.external.tinyrpc.dispatch import RPCDispatcher, ServerError
from indyva.core import Singleton
from indyva.core.context import Context
from .front import Front, ContextFreeFront


class Dispatcher(RPCDispatcher, Singleton):
    '''
    This class centralizes the access to the provided services
    '''

    def __init__(self):
        RPCDispatcher.__init__(self)

        self.context_free_front = ContextFreeFront.instance()

        self._middlewares = []

    def instert_middleware(self, index, middleware):
        self._middlewares.insert(index, middleware)

    def handle_request(self, request):
        _context = request.kwargs.pop('_context', None)
        _params = request.kwargs.pop('_params', None)
        if _params:
            request.args = _params
        return _context

    def _dispatch(self, request):
        try:
            _context = self.handle_request(request)

            front = None
            if self.context_free_front.has_method(request.method):
                front = self.context_free_front

            return self.dipatch_in_contex(request, _context, front)
        except Exception:
            # unexpected error, do not let client know what happened
            return request.error_respond(ServerError("Error processing the context:\n"
                                                     + str(_context)))

    def dipatch_in_contex(self, request, _context, front):
        with closing(Context.instance().open(_context)):
            for middleware in self._middlewares:
                middleware.run(_context)
            print "----------------------------------->"
            print "**", _context
            print "** active session:", Context.instance().active_session
            front = Front.instance() if front is None else front
            response = front._dispatch(request)
            print "<-----------------------------------"
        return response
