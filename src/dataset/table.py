'''
Created on 26/03/2013

@author: crispamares
'''
from abc_table import ITable
from mongo_backend.table import MongoTable

class Table(ITable):
    _backend = MongoTable
    
    def _prepare_data(self, data):
        self._backend._prepare_data(data)
