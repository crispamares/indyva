# -*- coding: utf-8 -*-
'''
Created on Oct 25, 2012

@author: crispamares
'''


import sys
import ujson  # https://github.com/Komnomnomnom/ultrajson

from analysis_data.data_store import DataStore
from analysis_data.table import Table

from autobahn.wamp import exportRpc

class RPCDataStore(DataStore):
    
    def __init__(self):
        DataStore.__init__(self)
        self.database_name = 'test_scinfo_db'

    @exportRpc
    def load_data(self, analysis_name):
        DataStore.load_data(self, analysis_name)
        return ujson.encode(self.data_source, orient='split')

def populate_factory(factory):
    factory.add_rpc_class('data_store', RPCDataStore)

