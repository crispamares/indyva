'''
Created on Jul 19, 2013

@author: crispamares
'''

from table import Table
from functools import partial
from dataset.abc_table import ITableView

class TableService(object):
    '''
    This class provide a facade for managing table objects
    '''

    def __init__(self, name='TableSrv'):
        '''
        @param name: The unique name of the service
        '''
        self._tables = {}
        self._name = name

    @property
    def name(self):
        return self._name
    
    def register_in(self, dispatcher):
        dispatcher.add_method(self.new_table)
        dispatcher.add_method(self.del_table)
        # TableView properties
        dispatcher.add_method(partial(self._proxy_property, 'name'), 'name')
        dispatcher.add_method(partial(self._proxy_property, 'index'), 'index')
        dispatcher.add_method(partial(self._proxy_property, 'view_args'), 'view_args')
        # TableView methods
        dispatcher.add_method(partial(self._proxy, 'get_data'), 'get_data')
        dispatcher.add_method(partial(self._proxy, 'find'), 'find')
        dispatcher.add_method(partial(self._proxy, 'find_one'), 'find_one')
        dispatcher.add_method(partial(self._proxy, 'row_count'), 'row_count')
        dispatcher.add_method(partial(self._proxy, 'column_count'), 'column_count')
        dispatcher.add_method(partial(self._proxy, 'column_names'), 'column_names')
        # Table methods
        dispatcher.add_method(partial(self._proxy, 'data'), 'data')
        dispatcher.add_method(partial(self._proxy, 'insert'), 'insert')
        dispatcher.add_method(partial(self._proxy, 'update'), 'update')
        dispatcher.add_method(partial(self._proxy, 'remove'), 'remove')
        dispatcher.add_method(partial(self._proxy, 'add_column'), 'add_column')
        dispatcher.add_method(partial(self._proxy, 'add_derived_column'), 'add_derived_column')
        
    def _proxy(self, method, table_name, *args, **kwargs):
        table = self._tables[table_name]
        result = table.__getattribute__(method)(*args, **kwargs)
        if isinstance(result, ITableView):
            self._tables[result.name] = result
        return result
    
    def _proxy_property(self, method, table_name):
        table = self._tables[table_name]
        result = table.__getattribute__(method)
        if isinstance(result, ITableView):
            self._tables[result.name] = result
        return result
        
    def new_table(self, name, data, schema=None):
        new_table = Table(name, schema).data(data)
        self._tables[name] = new_table
        return new_table

    def del_table(self, name):
        self._tables.pop(name)
    
    def __getattr__(self, name):
        if name in ['name', 'index', 'view_args']:
            return partial(self._proxy_property, name)
        else:
            return partial(self._proxy, name)
