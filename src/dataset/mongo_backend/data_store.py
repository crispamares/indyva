'''
Directory is a collection of metadata
metadata = {analysis_name: String,
            data_source: {type: 'csv' | 'mongo',
                          params: data_source_params
                         },
            filter_selection: [selection_params]
            mark_selection: [mark_selection_params]
           }
'''
import config
import pymongo
from data_source import create_data_source

class DataStore(object):
    '''The DataStore provides access to saved analysis'''
    __mongo_host = config.declare_config_variable(name='mongo_host', default='localhost')
    __mongo_port = config.declare_config_variable(name='mongo_port', default=27017)
    __database_name = config.declare_config_variable(name='database', default='scinfo')
    __directory_collection_name = config.declare_config_variable(name='directory_collection', default='directory')
    
    def __init__(self):
        self.data_source = None
        self.table = None
        self.filter_selection = None
        self.mark_selection = None

    @property
    def mongo_host(self):
        return self.__mongo_host

    @property
    def mongo_port(self):
        return self.__mongo_port

    @property
    def database_name(self):
        return self.__database_name

    @property
    def directory_collection_name(self):
        return self.__directory_collection_name

    @mongo_host.setter
    def mongo_host(self, value):
        self.__mongo_host = value

    @mongo_port.setter
    def mongo_port(self, value):
        self.__mongo_port = value

    @database_name.setter
    def database_name(self, value):
        self.__database_name = value

    @directory_collection_name.setter
    def directory_collection_name(self, value):
        self.__directory_collection_name = value
    
    def load_data(self, analysis_name):
        connection = pymongo.connection.Connection(self.mongo_host, self.mongo_port)
        db = connection[self.database_name]
        directory = db[self.directory_collection_name]
        metadata = directory.find_one({'analysis_name': analysis_name})
        
        print '***', metadata, directory
        self.data_source = create_data_source(metadata['data_source']['type'], metadata['data_source']['params'])
        # TODO load the filters
        # TODO load the marks

        return self.data_source

    
    def create_analysis_data(self):
        pass
    
        
    
    
        # TODO create the table
         
if __name__ == '__main__':
    ds = DataStore()
    
    



