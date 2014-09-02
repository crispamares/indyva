# -*- coding: utf-8 -*-
'''
Created on 07/06/2013

@author: jmorales
'''
import unittest

import pandas as pn
import json
from collections import OrderedDict

from indyva.dataset import RSC_DIR
from indyva.dataset.table import Table, TableView


class Test(unittest.TestCase):

    def callback(self, topic, msg):
        print topic, msg
        self.callback_executed = True

    def setUp(self):
        self.df = pn.read_csv(RSC_DIR + '/census.csv')
        with open(RSC_DIR + '/schema_census') as f:
            schema = json.loads(f.read())

        self.schema = OrderedDict(attributes=schema['attributes'], index=schema['index'])
        self.callback_executed = False

    def testCreationAsList(self):
        data = []
        for i in range(len(self.df)):
            data.append(self.df.ix[i].to_dict())

        Table('census', self.schema).data(data)

    def testCreationAsDataFrame(self):
        data = self.df
        Table('census', self.schema).data(data)

    def testCreationWithoutSchema(self):
        Table('census')

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

    def testMultiFind(self):
        table = Table('census', self.schema).data(self.df)
        view = table.find({'$or':[{'State': 'NY'},{'State': 'DC'}]})
        view2 = view.find({'Information':{'$gt': 200000}})
        self.assertIsInstance(view, TableView)
        for result in view.get_data():
            self.assertIn(result['State'], ['DC','NY'])
        for result in view2.get_data():
            self.assertNotIn(result['State'], ['DC'])

    def testDistinct(self):
        table = Table('census', self.schema).data(self.df)
        table.insert({'State': 'DC', 'life_meaning':42})
        view = table.find({'$or':[{'State': 'NY'},{'State': 'DC'},{'State': 'CA'}]})

        distincts = view.distinct('State')
        self.assertEqual(len(distincts), 3)
        for result in distincts:
            self.assertIn(result, ['DC','NY','CA'])

        distinct_view = view.distinct('State', as_view=True)
        self.assertIsInstance(distinct_view, TableView)
        result = distinct_view.get_data(outtype='c_list')
        self.assertEqual(result, {'State': ['NY', 'DC', 'CA']})

        view2 = view.find({'Information':{'$gt': 200000}})
        result = view2.distinct('State')
        self.assertEqual(result, ['NY', 'CA'])

    def testIndexItems(self):
        table = Table('census', self.schema).data(self.df)
        table.insert({'State': 'DC', 'life_meaning':42})
        view = table.find({'$or':[{'State': 'NY'},{'State': 'DC'}]})
        self.assertIsInstance(view, TableView)
        distincts = view.index_items()
        self.assertEqual(len(distincts), 2)
        for result in distincts:
            self.assertIn(result, ['DC','NY'])

    def testRowCount(self):
        table = Table('census', self.schema).data(self.df)
        self.assertEqual(table.row_count(), 51)
        view = table.find({'$or':[{'State': 'NY'},{'State': 'DC'}]})
        self.assertEqual(view.row_count(), 2)
        view2 = view.find({'State': 'NY'})
        self.assertEqual(view2.row_count(), 1)

    def testColumnCount(self):
        table = Table('census', self.schema).data(self.df)
        self.assertEqual(table.column_count(), 22)
        view = table.find({}, {'Information':True, 'State':True})
        self.assertEqual(view.column_count(), 2)
        view2 = view.find({}, {'State':True})
        self.assertEqual(view2.column_count(), 1)

    def testColumnNames(self):
        table = Table('census', self.schema).data(self.df)
        self.assertEqual(len(table.column_names()), 22)
        view = table.find({}, {'Information':True, 'State':True})
        self.assertEqual(view.column_names(), ['Information', 'State'])
        view2 = view.find({}, {'State':True})
        self.assertEqual(view2.column_names(), ['State'])

    def testCheckIndex(self):
        table = Table('census', self.schema).data(self.df)
        with self.assertRaises(ValueError):
            table._check_index({'life_meaning':42})
        table._check_index({'State': 'ES', 'life_meaning':42})

    def testIndex(self):
        table = Table('census', self.schema).data(self.df)
        self.assertEqual(table.index, 'State')

    def testInsert(self):
        table = Table('census', self.schema).data(self.df)
        c1 = table.row_count()
        table.insert({'State': 'ES', 'life_meaning':42})
        self.assertEqual(table.row_count() - c1, 1)

        c2 = table.row_count()
        table.insert([{'State': 'ES', 'life_meaning':42},
                      {'State': 'ES2', 'life_meaning':42},])
        self.assertEqual(table.row_count() - c2, 2)

        view = table.find({'life_meaning': {'$exists':True}})
        self.assertEqual(view.row_count(), 3)
        self.assertEqual(table.find_one({'life_meaning': {'$exists':True}})['life_meaning'], 42)

    def testAddEvent(self):
        table = Table('census', self.schema).data(self.df)
        table.subscribe_once('add', self.callback)
        self.callback_executed = False
        table.insert({'State': 'ES', 'life_meaning':42})
        self.assertTrue(self.callback_executed)

    def testUpdate(self):
        table = Table('census', self.schema).data(self.df)
        val = table.find_one({'State': 'DC'}, {'Information':True})['Information']
        val -= 2000
        table.update({'State': 'DC'}, {'$set': {'Information':val}})
        self.assertEqual(table.find_one({'State': 'DC'}, {'Information':True})['Information'], val)

    def testUpdateEvent(self):
        table = Table('census', self.schema).data(self.df)
        table.subscribe_once('update', self.callback)
        self.callback_executed = False
        table.update({'State': 'DC'}, {'$set': {'Information':2000}})
        self.assertTrue(self.callback_executed)

    def testRemove(self):
        table = Table('census', self.schema).data(self.df)
        query = {'State': 'DC'}
        c1 = table.find(query).row_count()
        table.remove(query)
        self.assertGreater(c1, table.find(query).row_count())

    def testRemoveEvent(self):
        table = Table('census', self.schema).data(self.df)
        query = {'State': 'DC'}
        table.subscribe_once('remove', self.callback)
        self.callback_executed = False
        table.remove(query)
        self.assertTrue(self.callback_executed)

if __name__ == "__main__":
    unittest.main()
