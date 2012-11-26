# -*- coding: utf-8 -*-
'''
Created on Oct 25, 2012

@author: crispamares
'''


import sys
from twisted.python import log
from twisted.internet import reactor

from autobahn.websocket import listenWS
from autobahn.wamp import  WampServerFactory, WampServerProtocol

# RPC modules
import data_store

DOMAIN = 'http://scinfo.io'

class ScinfoServerProtocol(WampServerProtocol):

    def onSessionOpen(self):
        for name, rpc_object in self.factory._rpc_objects.items():
            print '**** registering %s' % name
            self.registerForRpc(rpc_object, DOMAIN+"/%s#" % name)


class ScinfoServerFactory(WampServerFactory):

    def __init__(self, url, debugWamp=False):
        WampServerFactory.__init__(self, url, debugWamp=debugWamp)
        self._population_list = []  # [(name, rpc_class)]
        self._rpc_objects = {}      # {name: rpc_object}
            
    def build_rpc_objects(self):
        for name, rpc_class in self._population_list:
            self._rpc_objects[name] = rpc_class()

    def add_rpc_class(self, name, rpc_class):
        self._population_list.append( (name, rpc_class) )


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

    factory = ScinfoServerFactory("ws://localhost:9000", debugWamp=debug)

    # Populate factory with all the RPC modules
    data_store.populate_factory(factory)

    factory.build_rpc_objects()
    factory.protocol = ScinfoServerProtocol
    factory.setProtocolOptions(allowHixie76=True)
    listenWS(factory)

    reactor.run()
