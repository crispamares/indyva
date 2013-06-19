'''
Created on 26/03/2013

@author: crispamares
'''
from abc_table import ITable, ITableView
from mongo_backend.table import MongoTable

class TableView(ITableView):
    _backend = MongoTable

    def __init__(self, parent, view_args):
        if parent is not None:
            self._backend = parent._backend
        ITableView.__init__(self, parent, view_args)

    def get_data(self, outtype='list'):
        return self._backend.get_view_data(view_args=self.view_args, outtype='rows')
    
    def find(self, query=None, projection=None, skip=0, limit=0, sort=None):
        view_args = dict(query=query, projection=projection, skip=skip, limit=limit, sort=sort)
        return TableView(parent=self, view_args=view_args)

    def find_one(self, *args, **kwargs):
        return self._backend.find_one(*args, **kwargs)
    
    def count(self):
        return self._backend.count(self.view_args)


class Table(ITable, TableView):
    _backend = MongoTable

    def __init__(self, name='unnamed', schema=None):
        self._backend = self._backend(name, schema)
        ITable.__init__(self, name, schema)
        TableView.__init__(self, None, None)
        
    def data(self, data):
        ''' SetUp the data  
        @param data: Tabular data. Supported forms are: dict, DataFrame
        @return: self
        '''
        self._backend.data(data)
        return self
    
    def insert(self, row_or_rows):
        self._backend.insert(row_or_rows)
        
    def update(self):
        pass
    
    def remove(self):
        pass
    def add_column(self):
        pass
    def add_derived_column(self):
        pass
