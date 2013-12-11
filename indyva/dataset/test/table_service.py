# -*- coding: utf-8 -*-
'''
Created on 07/06/2013

@author: jmorales
'''
import unittest
from ..table_service import TableService
from external.tinyrpc.dispatch import RPCDispatcher
from external.tinyrpc.protocols.jsonrpc import JSONRPCRequest

import pandas as pn
import json
from collections import OrderedDict
from dataset import RSC_DIR
import exceptions
from dataset.table import TableView, Table
import names

class Test(unittest.TestCase):

    def callback(self, topic, msg):
        print topic, msg
        self.callback_executed = True

    def setUp(self):
        self.df = pn.read_csv(RSC_DIR+'/census.csv')
        with open(RSC_DIR+'/schema_census') as f:
            schema = json.loads(f.read())
        
        self.schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])
        self.callback_executed = False
        
        self.dispatcher = RPCDispatcher()
        self.service = TableService()
        self.service.register_in(self.dispatcher)
        
        # Create a table
        data = self.df
        self.service.new_table('_census', data, self.schema)
        
    def tearDown(self):
        names.clear()
        
    def testCreationAsList(self):
        data = []
        for i in range(len(self.df)):
            data.append(self.df.ix[i].to_dict())
           
        self.service.new_table('census', data, self.schema)
        
        request = JSONRPCRequest()
        request.method = 'new_table'
        request.args = 'census2', data, self.schema
        self.dispatcher.dispatch(request)
        

    def testCreationAsDataFrame(self):
        data = self.df
        self.service.new_table('census', data, self.schema)
        
        request = JSONRPCRequest()
        request.method = 'new_table'
        request.args = 'census2', data, self.schema
        self.dispatcher.dispatch(request)

    def testGetData(self):
        res = self.service.get_data('_census')
        self.assertEqual(len(res), len(self.df))

        request = JSONRPCRequest()
        request.method = 'get_data'
        request.args = ['_census']
        request.unique_id = 1
        res = self.dispatcher.dispatch(request).result
        self.assertEqual(len(res), len(self.df))

    def testFindOne(self):
        result = self.service.find_one('_census', {'$or':[{'State': 'NY'},{'State': 'DC'}]})
        self.assertIsInstance(result, dict)
        self.assertIn(result['State'], ['DC','NY'])

    def testFind(self):
        view = self.service.find('_census', {'$or':[{'State': 'NY'},{'State': 'DC'}]})
        self.assertIsInstance(view, TableView)
        for result in view.get_data():
            self.assertIn(result['State'], ['DC','NY'])

    def testRowCount(self):
        self.assertEqual(self.service.row_count('_census'), 51)
        view = self.service.find('_census',{'$or':[{'State': 'NY'},{'State': 'DC'}]})
        self.assertEqual(view.row_count(), 2)

    def testColumnCount(self):
        self.assertEqual(self.service.column_count('_census'), 22)
        view = self.service.find('_census', {}, {'Information':True})
        self.assertEqual(view.column_count(), 1)
        
    def testColumnNames(self):
        self.assertEqual(len(self.service.column_names('_census')), 22)
        view = self.service.find('_census', {}, {'Information':True})
        self.assertEqual(view.column_names(), ['Information'])
        
    def testCheckIndex(self):
        with self.assertRaises(ValueError):
            self.service._check_index('_census', {'life_meaning':42})
        self.service._check_index('_census', {'State': 'ES', 'life_meaning':42})
        
    def testIndex(self):
        self.assertEqual(self.service.index('_census'), 'State')
                
    def testInsert(self):
        
        c1 = self.service.row_count('_census')
        self.service.insert('_census', {'State': 'ES', 'life_meaning':42})
        self.assertEqual(self.service.row_count('_census') - c1, 1)

        c2 = self.service.row_count('_census')
        self.service.insert('_census', 
                            [{'State': 'ES', 'life_meaning':42},
                             {'State': 'ES2', 'life_meaning':42},])
        self.assertEqual(self.service.row_count('_census') - c2, 2)
        
        view = self.service.find('_census', {'life_meaning': {'$exists':True}})
        self.assertEqual(view.row_count(), 3)
        self.assertEqual( self.service.find_one('_census', {'life_meaning': {'$exists':True}})['life_meaning'], 42)
        
    def testAddEvent(self):
        table = Table('census', self.schema).data(self.df)
        table.subscribe_once('add', self.callback)
        self.callback_executed = False
        table.insert({'State': 'ES', 'life_meaning':42})
        self.assertTrue(self.callback_executed)
        
    def testUpdate(self):
        val = self.service.find_one('_census', {'State': 'DC'}, {'Information':True})['Information']
        val -= 2000
        self.service.update('_census', {'State': 'DC'}, {'$set': {'Information':val}})
        self.assertEqual(self.service.find_one('_census', {'State': 'DC'}, {'Information':True})['Information'], val)

    def testUpdateEvent(self):
        # TODO: ¿Do the table service provide subscribing facilities
        table = Table('census', self.schema).data(self.df)
        table.subscribe_once('update', self.callback)
        self.callback_executed = False
        table.update({'State': 'DC'}, {'$set': {'Information':2000}})
        self.assertTrue(self.callback_executed)
        
    def testRemove(self):
        
        query = {'State': 'DC'}
        c1 = self.service.find('_census', query).row_count()
        self.service.remove('_census', query)
        self.assertGreater(c1, self.service.find('_census', query).row_count())
    
    def testRemoveEvent(self):
        # TODO: Do the table service provide subscribing facilities?
        table = Table('census', self.schema).data(self.df)
        query = {'State': 'DC'}
        table.subscribe_once('remove', self.callback)
        self.callback_executed = False
        table.remove(query)
        self.assertTrue(self.callback_executed)
        
        
        
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testConstructor']
    unittest.main()