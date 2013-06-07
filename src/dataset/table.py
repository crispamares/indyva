'''
Created on 26/03/2013

@author: crispamares
'''
from abc_table import ITable, ITableView
from mongo_backend.table import MongoTable

class Table(ITable):
    _backend = MongoTable
    
    def _prepare_data(self, data):
        self._backend._prepare_data(data)

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

    def to_dict(self):
        pass

    def to_DataFrame(self):
        pass

    def find(self, *args, **kwargs):
        return TableView(parent=self, **kwargs)

    def find_one(self):
        pass
    
    def count(self):
        pass
