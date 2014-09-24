'''
'''

from indyva.core.names import INamed
from .table_io import read_csv


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
        self._dispatcher = None

    def register_in(self, dispatcher):
        self._dispatcher = dispatcher

        dispatcher.add_method(self.read_csv)

    def read_csv(self, table_name, filepath, schema=None, *args, **kwargs):
        table = read_csv(table_name, filepath, schema, *args, **kwargs)
        self._dispatcher.get_method(self._table_srv_name + '.expose_table')(table)
