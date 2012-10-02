'''
Created on Sep 29, 2012

@author: crispamares
'''
import unittest
from data_store import DataStore

class Test(unittest.TestCase):


    def setUp(self):
        self.data_store = DataStore()


    def tearDown(self):
        pass


    def test_create_data_source(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()