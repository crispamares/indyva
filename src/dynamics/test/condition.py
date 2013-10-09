'''
Created on Oct 9, 2013

@author: crispamares
'''
import unittest

import pandas as pd
from dataset import RSC_DIR
import json
from collections import OrderedDict
from dataset.table import Table

from dynamics.condition import CategoricalCondition

class Test(unittest.TestCase):

    def setUp(self):
        self.df = pd.read_csv(RSC_DIR+'/census.csv')
        with open(RSC_DIR+'/schema_census') as f:
            schema = json.loads(f.read())
        
        self.schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])
        self.table = Table('census', self.schema).data(self.df)
        
        self.table.add_column('fake_cat', 'CATEGORICAL')
        items = self.table.index_items()
        fake_cat = ['C1','C2','C3','C4']
        for i, item in enumerate(items):
            self.table.update({'State':item}, {'$set': {'fake_cat': fake_cat[ i % 4]}})

    def testCreation(self):
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        self.assertEqual(cc.included_categories(), [])
        
        with self.assertRaises(NotImplementedError):
            cc = CategoricalCondition(data=self.table, attr='Information')
        
    def testAdd(self):
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        cc.add_category('C1')
        self.assertEqual(set(cc.included_categories()), set(['C1']))
        cc.add_category(['C1', 'C3'])
        self.assertEqual(set(cc.included_categories()), set(['C1', 'C3']))

    def testRemove(self):
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        cc.add_category(['C1', 'C3'])
        cc.remove_category('C1')
        self.assertEqual(set(cc.included_categories()), set(['C3']))

    def testIncludeAll(self):
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        cc.incude_all()
        self.assertSetEqual(set(cc.included_categories()),
                            set(self.table.distinct('fake_cat')))

    def testExcludeAll(self):
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        cc.add_category('C1')
        cc.exclude_all()
        self.assertEqual(cc.included_categories(),[])
        
    def testToggle(self):
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        cc.add_category('C1')
        cc.toggle()
        self.assertEqual(set(cc.included_categories()), set(['C2', 'C3', 'C4']))
        
    def testIncludedItems(self):
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        cc.add_category('C1')
        self.assertSetEqual(set(cc.included_items()),
                         set(['AK', 'CA', 'DE', 'IA', 'KS', 'MD', 'MO',
                           'ND', 'NM', 'OK', 'SC', 'UT', 'WI']))
        cc.add_category(['C2', 'C3', 'C4'])
        self.assertSetEqual(set(cc.included_items()), set(self.table.distinct('State')))

    def testExcludedItems(self):
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        cc.add_category(['C2', 'C3', 'C4'])
        self.assertSetEqual(set(cc.excluded_items()),
                         set(['AK', 'CA', 'DE', 'IA', 'KS', 'MD', 'MO',
                           'ND', 'NM', 'OK', 'SC', 'UT', 'WI']))
        cc.add_category('C1')
        self.assertSetEqual(set(cc.excluded_items()), set([]))
                            
                            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCreation']
    unittest.main()