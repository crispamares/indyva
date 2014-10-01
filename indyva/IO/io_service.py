'''
'''

from indyva.core.names import INamed
from .table_io import read_csv
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

    def read_csv(self, table_name, filepath, schema=None, *args, **kwargs):
        table = read_csv(table_name, filepath, schema, *args, **kwargs)
        case = Showcase.instance().get_case(table.__class__.__name__)
        case[table.oid] = table
        return table
