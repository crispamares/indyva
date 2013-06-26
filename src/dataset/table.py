'''
Created on 26/03/2013

@author: crispamares
'''
from abc_table import ITable, ITableView
from epubsub.abc_publisher import IPublisher 
from epubsub.bus import Bus

from mongo_backend.table import MongoTable

class TableView(ITableView, IPublisher):
    _backend = MongoTable

    def __init__(self, parent, view_args):
        if parent is not None:
            self._backend = parent._backend
            bus = parent._bus
        else:
            bus = Bus(prefix= self.name+'.')

        topics = ['add', 'update', 'remove']
        IPublisher.__init__(self, bus, topics)
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
        #TODO: Improve the message
        self._backend.insert(row_or_rows)
        msg = {'n_rows_added':len(row_or_rows)}
        self._bus.publish('add', msg)
                
    def update(self, query=None, update=None, multi=True, upsert=False):
        #TODO: Improve the message
        self._backend.update(query, update, multi, upsert)
        msg = {'n_updated':None}
        self._bus.publish('update', msg)
        
    def remove(self, query):
        #TODO: Improve the message
        self._backend.remove(query)
        msg = {'n_removed':None}
        self._bus.publish('remove', msg)
        
    def add_column(self, name, attribute_schema):
        ''' Add a new column schema to the table
        @param name: str The name of the new column. Two columns with the same 
        name are not allowed 
        @param attribute_schema: AttributeSchema
        '''
        self._schema.add_attribute(name, attribute_schema)
    
    def add_derived_column(self, name, attribute_schema, inputs, function):
        '''
        @param name: str The name of the new column. Two columns with the same 
        name are not allowed 
        @param attribute_schema: AttributeSchema
        @param inputs: list with the names of the attributes that will be the 
        inputs for the function that computes the derived value. Allways that
        those inputs change the derived column values are recomputed
        @function: dict or RemoteFunction This code will be executed once per row
        Returns the derived value. The dict statement use the core grammar and has
        access to the inputs with $name_of_input. The RemoteFunction will be 
        invoked with a dict of inputs {name_of_input:value}      
        '''
        pass
