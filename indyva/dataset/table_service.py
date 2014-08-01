'''
Created on Jul 19, 2013

@author: crispamares
'''

from functools import partial

from indyva.names import INamed
from indyva.facade.showcase import Case
from .table import Table
from .abc_table import ITableView

class TableService(INamed):
    '''
    This class provide a facade for managing table objects
    '''

    def __init__(self, name='TableSrv'):
        '''
        @param name: The unique name of the service
        '''
        self._tables = Case()
        INamed.__init__(self, name)
    
    def register_in(self, dispatcher):
        dispatcher.add_method(self.new_table)
        dispatcher.add_method(self.expose_table)
        dispatcher.add_method(self.del_table)
        # TableView properties
        dispatcher.add_method(partial(self._proxy_property, 'name'), 'name')
        dispatcher.add_method(partial(self._proxy_property, 'index'), 'index')
        dispatcher.add_method(partial(self._proxy_property, 'view_args'), 'view_args')
        # TableView methods
        dispatcher.add_method(partial(self._proxy, 'get_data'), 'get_data')
        dispatcher.add_method(partial(self._proxy, 'find'), 'find')
        dispatcher.add_method(partial(self._proxy, 'find_one'), 'find_one')
        dispatcher.add_method(partial(self._proxy, 'distinct'), 'distinct')
        dispatcher.add_method(partial(self._proxy, 'aggregate'), 'aggregate')
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
        
    def _proxy(self, method, table_oid, *args, **kwargs):
        table = self._tables[table_oid]
        result = table.__getattribute__(method)(*args, **kwargs)
        if isinstance(result, ITableView):
            self._tables[result.oid] = result
        return result
    
    def _proxy_property(self, method, table_oid):
        table = self._tables[table_oid]
        result = table.__getattribute__(method)
        if isinstance(result, ITableView):
            self._tables[result.oid] = result
        return result
        
    def new_table(self, name, data, schema=None, prefix='ds:'):
        '''
        :param str name: If a name is not provided, an uuid is generated
        :param dict data: A list of dicts, each dict is a row. 
        :param schema: The schema associated to the data.  
        :param str prefix: Prepended to the name creates the oid 
        '''
        new_table = Table(name, schema, prefix=prefix).data(data)
        self._tables[new_table.oid] = new_table
        return new_table

    def expose_table(self, table):
        self._tables[table.oid] = table
        return table

    def del_table(self, oid):
        self._tables.pop(oid)
    
    def __getattr__(self, method):
        if method in ['name', 'index', 'view_args']:
            return partial(self._proxy_property, method)
        else:
            return partial(self._proxy, method)
