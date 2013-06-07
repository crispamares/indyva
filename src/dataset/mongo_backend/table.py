from __future__ import absolute_import
from ..abc_table import ITable
from .connection import Connection

import pandas as pn

''' The mongo backend stores each analysis as a different database. And 
each dataset as a different collection.

The database used as analysis namespace is setted in the connection module
'''

class MongoTable(ITable):
    
    def __init__(self, *args, **kargs):
        self.connection = Connection()
        self._col = None
        ITable.__init__(self, *args, **kargs)

    def get_data(self , outtype='rows'):
        return list(self.find({}))

    def data(self, data):
        db = self.connection.db
        db.drop_collection(self.name)
        self._col = db[self.name]
        
        rows = []
        if isinstance(data, pn.DataFrame):
            for i in range(len(data)):
                rows.append(data.ix[i].to_dict())
        elif isinstance(data, list):
            rows = data
        
        self._col.insert(rows)
        return self
    
    def find(self, spec=None, attributes=None, skip=0, limit=0, sort=None):
        return self._col.find(spec=spec, fields=attributes, skip=skip, limit=limit, sort=sort)
        
    def find_one(self):
        pass
    
    def count(self):
        pass

        

