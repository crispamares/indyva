import config
import pymongo
from data_source import create_data_source

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

class DataStore(object):
    
    mongo_host = config.declare_config_variable(name='mongo_host', default='localhost')
    mongo_port = config.declare_config_variable(name='mongo_port', default=27017)
    database_name = config.declare_config_variable(name='database', default='scinfo')
    directory_collection_name = config.declare_config_variable(name='directory_collection', default='directory')
    
    def __init__(self):
        self.data_source = None
        self.table = None
        self.filter_selection = None
        self.mark_selection = None
    
    def load_data(self, analysis_name):
        connection = pymongo.connection.Connection(self.mongo_host, self.mongo_port)
        db = connection[self.database_name]
        directory = db[self.directory_collection_name]
        metadata = directory.find_one({'analysis_name': analysis_name})
        
        print '***', metadata, directory
        self.data_source = create_data_source(metadata['data_source']['type'], metadata['data_source']['params'])
        # TODO load the filters
        # TODO load the marks

    
    def create_analysis_data(self):
        pass
    
    
        # TODO create the table
         
    
    



