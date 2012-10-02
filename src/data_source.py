import pandas as pn
import pymongo

class CSVDataSource(object):
    def __init__(self, file_name, config={}):
        '''
        This class loads csv files 
        @param file_name: String
        @param config: A dictionary with pandas.read_csv arguments
        '''
        self.file_name = file_name
        self.config = config

    def load(self):
        '''
        This method loads the content of the file and returns a DataFrame
        @return: pandas.DataFrame
        '''
        df = pn.read_csv(self.file_name, **self.config)
        return df


class MongoDataSource(object):
    def __init__(self, database, collection, find={}, columns={'_id':False}):
        '''
        This class loads tables saved in a collection of a Mongo database
        @param database: String name of the database
        @param collection: String name of the collection
        @param find: Dictionary The argument to the find() method.
        @param columns: Dicttionay The columns argument in the find() method
        '''
        self.database = database
        self.collection = collection
        self.find = find
        self.columns = columns

    def _query(self):
        '''
        This method execute the query to the database.
        '''
        conect = pymongo.connection.Connection()
        db = conect[self.database]
        coll = db[self.collection]
        query_result = coll.find(self.find, self.columns)
        return query_result
        
    def load(self):
        '''
        This method loads the content of the file and returns a DataFrame.
        Reimplement this method if the data is not in a table
        @return: pandas.DataFrame
        '''
        query_result = list(self._query())
        df = pn.DataFrame(query_result)
        return df
    
    
        