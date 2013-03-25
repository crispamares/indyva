from table import ITable
import pymongo

''' The mongo backend stores each analysis as a different database. And 
each dataset as a different collection.

'''

class MongoTable(ITable):

    def _adquire_data(self, data):
        pass


