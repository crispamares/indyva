# -*- coding: utf-8 -*-
'''
Created on Oct 25, 2012

@author: crispamares
'''


import sys
import ujson  # https://github.com/Komnomnomnom/ultrajson

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import listenWS
from autobahn.wamp import exportRpc, \
                                  WampServerFactory, \
                                  WampServerProtocol

from analysis_data.data_store import DataStore
from analysis_data.table import Table

DOMAIN = 'http://scinfo.io'

class RPCDataStore(DataStore):
    
    @exportRpc
    def load_data(self, analysis_name):
        DataStore.load_data(self, analysis_name)
        return ujson.encode(self.data_source, orient='split')

class ScinfoServerProtocol(WampServerProtocol):

    def onSessionOpen(self):
        ## register the key-value store, which resides on the factory within
        ## this connection
        self.registerForRpc(self.factory.data_store, DOMAIN+"/data_store#")


class ScinfoServerFactory(WampServerFactory):

    def __init__(self, url, debugWamp=False):
        WampServerFactory.__init__(self, url, debugWamp=debugWamp)
        
        ## the key-value store resides on the factory object, since it is to
        ## be shared among all client connections
        self.data_store = RPCDataStore()
        self.data_store.database_name = 'test_scinfo_db'


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

    factory = ScinfoServerFactory("ws://localhost:9000", debugWamp=debug)
    factory.protocol = ScinfoServerProtocol
    factory.setProtocolOptions(allowHixie76=True)
    listenWS(factory)

    webdir = File(".")
    web = Site(webdir)
    reactor.listenTCP(8080, web)

    reactor.run()
