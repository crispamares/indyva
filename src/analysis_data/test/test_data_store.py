'''
Created on Sep 29, 2012

@author: crispamares
'''
import unittest
from analysis_data.data_store import DataStore
import pymongo
from __init__ import test_database

class Test(unittest.TestCase):

    def setUp(self):
        self.data_store = DataStore()
        self.data_store.database_name = test_database

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        super(Test, cls).setUpClass()
        cls.connection = pymongo.connection.Connection() 
        cls.db = cls.connection[test_database]
        cls.directory = cls.db['directory']

    def no_test_create_analysis_data(self):
        self.data_store.create_analysis_data('file://rsc/census.csv')
        self.data_store.create_analysis_data('mongodb://rsc/census.csv')
        
    
    def no_test_save_data(self):
        self.data_store.save_data('census')
        
    def test_load_data(self):
        self.data_store.load_data('distances')
        print self.data_store.data_source

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()