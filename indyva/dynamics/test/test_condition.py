'''
Created on Oct 9, 2013

@author: crispamares
'''
import unittest

import pandas as pd
import json
from collections import OrderedDict

from indyva.dataset.table import Table
from indyva.dataset import RSC_DIR
from indyva.dynamics.condition import CategoricalCondition, RangeCondition, QueryCondition
from indyva.core import names

class CategoricalTest(unittest.TestCase):

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

    def tearDown(self):
        names.clear()

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

    def testToggleItem(self):
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        cc.add_category(['C1', 'C3'])
        cc.toggle_category('C1')
        cc.toggle_category('C2')
        self.assertEqual(set(cc.included_categories()), set(['C3', 'C2']))
        cc.toggle_category(['C2','C4'])
        self.assertEqual(set(cc.included_categories()), set(['C3', 'C4']))

    def testIncludeAll(self):
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        cc.include_all()
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








class RangeTest(unittest.TestCase):

    def setUp(self):
        self.df = pd.read_csv(RSC_DIR+'/census.csv')
        with open(RSC_DIR+'/schema_census') as f:
            schema = json.loads(f.read())

        self.schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])
        self.table = Table('census', self.schema).data(self.df)

    def tearDown(self):
        names.clear()

    def testCreation(self):
        rc = RangeCondition(data=self.table, attr='Information')
        self.assertEqual(rc.domain['min'], rc.range['min'])
        self.assertEqual(rc.domain['max'], rc.range['max'])
        self.assertEqual(rc.range['relative_max'], 1)
        self.assertEqual(rc.range['relative_min'], 0)
        self.assertEqual(set(rc.included_items()), set(self.table.index_items()))

        rc2 = RangeCondition(data=self.table, attr='Information',
                             range=dict(min=250000, max=500000))
        self.assertEqual(rc2.domain['max'], rc2.range['max'])
        self.assertEqual(250000, rc2.range['min'])
        self.assertEqual(rc2.range['relative_max'], 1)
        self.assertNotEqual(rc2.range['relative_min'], 0)
        self.assertEqual(set(rc2.included_items()), set(['CA', 'NY']))

        rc3 = RangeCondition(data=self.table, attr='Information',
                             domain=dict(min=250000, max=500000))
        self.assertEqual(rc3.domain['min'], rc3.range['min'])
        self.assertEqual(rc3.domain['max'], rc3.range['max'])
        self.assertEqual(rc3.range['relative_max'], 1)
        self.assertEqual(rc3.range['relative_min'], 0)
        self.assertEqual(set(rc3.included_items()), set(['CA', 'NY']))

    def testIncludeAll(self):
        rc = RangeCondition(data=self.table, attr='Information',
                            range=dict(min=250000, max=500000))
        self.assertEqual(set(rc.included_items()), set(['CA', 'NY']))
        rc.include_all()
        self.assertEqual(set(rc.included_items()), set(self.table.index_items()))

    def testIncludedItems(self):
        rc = RangeCondition(data=self.table, attr='Information')
        self.assertEqual(set(rc.included_items()), set(self.table.index_items()))

    def testExcludedItems(self):
        rc = RangeCondition(data=self.table, attr='Information')
        self.assertItemsEqual(rc.excluded_items(), [])

        rc2 = RangeCondition(data=self.table, attr='Information',
                            range=dict(min=250000, max=500000))
        excluded = set(rc.included_items()) - set(['CA', 'NY'])
        self.assertEqual(set(rc2.excluded_items()), excluded)

    def testSetRange(self):
        rc = RangeCondition(data=self.table, attr='Information')
        self.assertItemsEqual(rc.included_items(), self.table.index_items())
        rc.set_range(min=250000)
        self.assertEqual(set(rc.included_items()), set(['CA', 'NY']))
        change = rc.set_range(max=250000)
        self.assertItemsEqual(rc.included_items(), [])
        self.assertEqual(change, {'included': [], 'excluded': [u'NY', u'CA']})
        with self.assertRaises(ValueError):
            rc.set_range()

        change = rc.set_range(0,1, relative=True)
        self.assertItemsEqual(rc.included_items(), self.table.index_items())
        self.assertItemsEqual(change['included'], rc.included_items())
        self.assertItemsEqual(change['excluded'], [])

        rc.set_range(0.5, relative=True)
        self.assertEqual(set(rc.included_items()), set(['CA', 'NY']))
        self.assertEqual(rc.range, {'max': 492737.0, 'min': 248347.0,
                                    'relative_max': 1.0, 'relative_min': 0.5})






class QueryTest(unittest.TestCase):

    def setUp(self):
        self.df = pd.read_csv(RSC_DIR + '/census.csv')
        with open(RSC_DIR + '/schema_census') as f:
            schema = json.loads(f.read())

        self.schema = OrderedDict(attributes=schema['attributes'], index=schema['index'])
        self.table = Table('census', self.schema).data(self.df)

    def tearDown(self):
        names.clear()

    def testCreation(self):
        qc = QueryCondition(data=self.table)
        self.assertEqual(qc.query, {})
        self.assertEqual(set(qc.included_items()), set(self.table.index_items()))

        qc2 = QueryCondition(data=self.table, query={'State':'NY'})
        self.assertEqual(set(qc2.included_items()), set(['NY']))

    def testIncludedItems(self):
        qc = QueryCondition(data=self.table)
        self.assertEqual(set(qc.included_items()), set(self.table.index_items()))

    def testExcludedItems(self):
        qc = QueryCondition(data=self.table)
        self.assertItemsEqual(qc.excluded_items(), [])

        qc2 = QueryCondition(data=self.table, query={'State':'NY'})
        excluded = set(qc.included_items()) - set(['NY'])
        self.assertEqual(set(qc2.excluded_items()), excluded)

if __name__ == "__main__":
    unittest.main()
