'''
Created on 26/03/2013

@author: crispamares
'''
from abc_table import ITable, ITableView
from epubsub.abc_publisher import IPublisher, pub_result
from epubsub.bus import Bus

from mongo_backend.table import MongoTable

class TableView(ITableView, IPublisher):
    _backend = MongoTable

    def __init__(self, parent, view_args):
        if parent is not None:
            self._backend = parent._backend
            self._schema = parent._schema
            bus = parent._bus
            self._name = self._new_name(parent.name) # New name for the created ViewTable
        else:
            bus = Bus(prefix= 'ds.'+self.name+'.')
        
        topics = ['add', 'update', 'remove']
        IPublisher.__init__(self, bus, topics)
        ITableView.__init__(self, parent, view_args)
        
    def get_data(self, outtype='rows'):
        return self._backend.get_view_data(view_args=self.view_args, outtype=outtype)
    
    def find(self, query=None, projection=None, skip=0, limit=0, sort=None):
        view_args = dict(query=query, projection=projection, skip=skip, limit=limit, sort=sort)
        return TableView(parent=self, view_args=view_args)

    def find_one(self, query=None, projection=None, skip=0, sort=None):
        view_args = dict(query=query, projection=projection, skip=skip, limit=1, sort=sort)
        return self._backend.find_one( view_args=self._merge_args(self.view_args, view_args) )xs
    
    def distinct(self, column, as_view=False):
        if not as_view:
            return self._backend.distinct(column, view_args=self.view_args)
        else:
            return self.aggregate([{'$group' : {'_id': '$'+column}},
                                   {'$project' : {column: '$_id'}}])
        
    def aggregate(self, pipeline):
        view_args = {'pipeline' : pipeline}
        return TableView(parent=self, view_args=view_args)
    
    def index_items(self):
        return self._backend.index_items(view_args=self.view_args)
    
    def row_count(self):
        return self._backend.row_count(view_args=self.view_args)

    def column_count(self):
        return self._backend.column_count(view_args=self.view_args)
    
    def column_names(self):
        return self._backend.column_names(view_args=self.view_args)
    
    def for_json(self):
        return self.name
    

class Table(ITable, TableView):
    _backend = MongoTable

    def __init__(self, name='unnamed', schema=None):
        self._backend = self._backend(name, schema)
        ITable.__init__(self, name, schema)
        TableView.__init__(self, None, None)
        
    def _check_index(self, row_or_rows):
        '''Raise a ValueError if any row does not have valid index keys'''
        rows = row_or_rows if isinstance(row_or_rows, list) else [row_or_rows]
        indices = self.index if isinstance(self.index, tuple) else tuple([self.index])
        for row in rows:
            if not all([row.has_key(i) for i in indices]):
                raise ValueError('Every row needs valid index: {0}'.format(indices))
        
    def data(self, data):
        ''' SetUp the data  
        @param data: Tabular data. Supported forms are: dict, DataFrame
        @return: self
        '''
        self._backend.data(data)
        return self

    @pub_result('add')
    def insert(self, row_or_rows):
        self._check_index(row_or_rows)
        msg = self._backend.insert(row_or_rows)
        return msg

    @pub_result('update')
    def update(self, query=None, update=None, multi=True, upsert=False):
        #TODO: Improve the message
        msg = self._backend.update(query, update, multi, upsert)
        return msg

    @pub_result('remove')
    def remove(self, query):
        msg = self._backend.remove(query)
        return msg
        
        
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
