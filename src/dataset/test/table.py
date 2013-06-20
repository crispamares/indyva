# -*- coding: utf-8 -*-
'''
Created on 07/06/2013

@author: jmorales
'''
import unittest
from dataset.table import Table, TableView
import pandas as pn
import json
from collections import OrderedDict
from dataset import RSC_DIR
import exceptions

class Test(unittest.TestCase):

    def setUp(self):
        self.df = pn.read_csv(RSC_DIR+'/census.csv')
        with open(RSC_DIR+'/schema_census') as f:
            schema = json.loads(f.read())
        
        self.schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])
        
    def testCreationAsList(self):
        data = []
        for i in range(len(self.df)):
            data.append(self.df.ix[i].to_dict())
           
        Table('census', self.schema).data(data)

    def testCreationAsDataFrame(self):
        data = self.df
        Table('census', self.schema).data(data)
        
    def testCreationWithoutSchema(self):
        self.assertRaises(exceptions.NotImplementedError, lambda: Table('census'))
        
    def testGetData(self):
        table = Table('census', self.schema).data(self.df)
        self.assertEqual(len(table.get_data()), len(self.df))

    def testFindOne(self):
        table = Table('census', self.schema).data(self.df)
        result = table.find_one({'$or':[{'State': 'NY'},{'State': 'DC'}]})
        self.assertIsInstance(result, dict)
        self.assertIn(result['State'], ['DC','NY'])

    def testFind(self):
        table = Table('census', self.schema).data(self.df)
        view = table.find({'$or':[{'State': 'NY'},{'State': 'DC'}]})
        self.assertIsInstance(view, TableView)
        for result in view.get_data():
            self.assertIn(result['State'], ['DC','NY'])

    def testCount(self):
        table = Table('census', self.schema).data(self.df)
        self.assertEqual(table.count(), 51)
        view = table.find({'$or':[{'State': 'NY'},{'State': 'DC'}]})
        self.assertEqual(view.count(), 2)
        
    def testInsert(self):
        table = Table('census', self.schema).data(self.df)
        c1 = table.count()
        table.insert({'life_meanning':42})
        self.assertEqual(table.count() - c1, 1)
        view = table.find({'life_meanning': {'$exists':True}})
        self.assertEqual(view.count(), 1)
        self.assertEqual( table.find_one({'life_meanning': {'$exists':True}})['life_meanning'], 42)
        
    def testUpdate(self):
        table = Table('census', self.schema).data(self.df)
        val = table.find_one({'State': 'DC'}, {'Information':True})['Information']
        val -= 2000
        table.update({'State': 'DC'}, {'$set': {'Information':val}})
        self.assertEqual(table.find_one({'State': 'DC'}, {'Information':True})['Information'], val)

    def testRemove(self):
        table = Table('census', self.schema).data(self.df)
        query = {'State': 'DC'}
        c1 = table.find(query).count()
        table.remove(query)
        self.assertGreater(c1, table.find(query).count())
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testConstructor']
    unittest.main()