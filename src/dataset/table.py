'''
Created on 26/03/2013

@author: crispamares
'''
from abc_table import ITable, ITableView
from mongo_backend.table import MongoTable

class Table(ITable):
    _backend = MongoTable

    def __init__(self, name='unnamed', schema=None):
        self._backend = self._backend(name, schema)
        ITable.__init__(self, name, schema)

    get_data = TableView.get_data
    
    def data(self, data):
        ''' SetUp the data  
        @param data: Tabular data. Supported forms are: dict, DataFrame
        @return: self
        '''
        self._backend.data(data)
        return self

    to_dict = TableView.to_dict
    to_DataFrame = TableView.to_DataFrame
    find = TableView.find
    find_one = TableView.find_one
    count = TableView.count
    
    def insert(self):
        pass
    def update(self):
        pass
    def remove(self):
        pass
    def add_column(self):
        pass
    def add_derived_column(self):
        pass
        

class TableView(ITableView):
    _backend = MongoTable

    def __init__(self, parent, find_args):
        self._backend = self._backend()
        ITableView.__init__(self, parent, find_args)

    def get_data(self, outtype='rows'):
        pass 
    
    def find(self, *args, **kwargs):
        return TableView(parent=self, **kwargs)

    def find_one(self):
        pass
    
    def count(self):
        pass
