'''
'''

from indyva.core.names import INamed
from .table_io import read_csv, write_csv
from indyva.facade.showcase import Showcase


class IOService(INamed):
    '''
    This class provide a facade for IO functions
    '''

    def __init__(self, name='IOSrv', table_srv_name='TableSrv'):
        '''
        @param name: The unique name of the service
        '''
        INamed.__init__(self, name)
        self._table_srv_name = table_srv_name

    def register_in(self, dispatcher):
        dispatcher.add_method(self.read_csv)
        dispatcher.add_method(self.write_csv)

    def read_csv(self, table_name, filepath, schema=None, *args, **kwargs):
        table = read_csv(table_name, filepath, schema, *args, **kwargs)
        case = Showcase.instance().get_case(self._table_srv_name)
        case[table.oid] = table
        return table

    def write_csv(self, table_name, filepath, schema=None, *args, **kwargs):
        case = Showcase.instance().get_case(self._table_srv_name)
        table = case[table_name]
        schema = schema if schema is not None else table.schema
        return write_csv(table, filepath, schema, *args, **kwargs)
