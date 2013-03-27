'''
Created on 26/03/2013

@author: crispamares
'''
import unittest
from dataset.mongo_backend.table import MongoTable

import pandas as pn
import json
from collections import OrderedDict
import exceptions

class Test(unittest.TestCase):

    def setUp(self):
        self.df = pn.read_csv('rsc/census.csv')
        with open('rsc/schema_census') as f:
            schema = json.loads(f.read())
        
        self.schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])

    def testCreationAsList(self):
        data = []
    
        for i in range(len(self.df)):
            data.append(self.df.ix[i].to_dict())
           
        MongoTable(data, 'census', self.schema)

    def testCreationAsDataFrame(self):
        data = self.df
        MongoTable(data, 'census', self.schema)
        
    def testCreationWithoutSchema(self):
        self.assertRaises(exceptions.NotImplementedError, lambda: MongoTable(self.df, 'census'))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCreation']
    unittest.main()