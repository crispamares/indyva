from indyva.dataset.shared_object import SharedObject
from indyva.epubsub.abc_publisher import pub_result

from .mongo_backend.shared_array import MongoSharedArray
    

class SharedArray(SharedObject):
    _backend = MongoTable

    def __init__(self, name, prefix=''):
        SharedObject.__init__(self, name=name, topics=['add', 'update', 'remove'], prefix=prefix)

    def data(self, data):
        ''' SetUp the data  
        :param list data: The data array to use, only basic types are supported 
        :return: self
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
        
        
    
