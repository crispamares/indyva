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

    def to_dict(self):
        self._backend.to_dict()

    def to_DataFrame(self):
        self._backend.to_DataFrame()

    def find(self, spec=None, attributes=None, skip=0, limit=0, sort=None):
        self._backend.find(spec, attributes, skip, limit, sort)

