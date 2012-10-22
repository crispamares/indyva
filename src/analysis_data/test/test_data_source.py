'''
Created on Sep 29, 2012

@author: crispamares
'''
import unittest
from analysis_data.data_source import CSVDataSource, MongoDataSource
import os

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_csv(self):
        file_name = os.path.join(os.path.dirname(__file__) ,'rsc/census.csv')
        source = CSVDataSource(file_name)
        df = source.load()
        self.assertEqual(df.shape, (51, 22))
        
    def no_test_mongo(self):
        db = 'synapses'
        coll = 'synapses'
        source = MongoDataSource(db, coll)
        df = source.load()
        print df
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()