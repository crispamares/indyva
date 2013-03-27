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
        super(MongoTable, self).__init__(*args, **kargs)

    def _prepare_data(self, data):
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
        
        
        

