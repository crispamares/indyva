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
from indyva.dynamics.condition import CategoricalCondition, RangeCondition,\
    AttributeCondition
from indyva.dynamics.condition_set import ConditionSet
from indyva import names


class ConditionSetTest(unittest.TestCase):

    def setUp(self):
        self.df = pd.read_csv(RSC_DIR+'/census.csv')
        with open(RSC_DIR+'/schema_census') as f:
            schema = json.loads(f.read())

        self.schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])
        self.table = Table('census', self.schema).data(self.df)

        self.table.add_column('fake_cat', 'CATEGORICAL')
        items = self.table.index_items()
        fake_cat = ['C1','C2','C3','C4']
        self.fake_sets = {}
        for k in fake_cat:
            self.fake_sets.setdefault(k, [])
        for i, item in enumerate(items):
            self.table.update({'State':item}, {'$set': {'fake_cat': fake_cat[ i % 4]}})
            self.fake_sets[fake_cat[ i % 4]].append(item)

    def tearDown(self):
        names.clear()

    def testCreation(self):
        cs = ConditionSet(name='condition_set', data=self.table, setop='AND')
        self.assertEqual(cs.is_empty(), True)
        self.assertEqual(cs.reference, [])
        self.assertEqual(cs.query, {'State': {'$in': []}})
        self.assertEqual(cs.projection, {})

    def testAddCondition(self):
        cs = ConditionSet(name='condition_set', data=self.table, setop='AND')
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        cs.add_condition(cc)
        cc.add_category('C1')
        self.assertItemsEqual(cs.reference, self.fake_sets['C1'])
        cc.add_category(['C1', 'C3'])
        c1_and_c3 = self.fake_sets['C1'][:]
        c1_and_c3 += self.fake_sets['C3']
        self.assertItemsEqual(cs.reference, c1_and_c3)

    def testAddSeveralConditions(self):
        cs = ConditionSet(name='condition_set', data=self.table, setop='AND')
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        rc = RangeCondition(data=self.table, attr='Information')
        rc.set_range(0.5, relative=True)

        cs.add_condition(cc)
        cc.add_category('C1')
        self.assertItemsEqual(cs.reference, self.fake_sets['C1'])

        cs.add_condition(rc)
        self.assertItemsEqual(cs.reference, ['CA'])

        cc.toggle_category(['C1', 'C3'])
        self.assertItemsEqual(cs.reference, ['NY'])

        rc.set_range(0, 1, relative=True)
        self.assertItemsEqual(cs.reference, self.fake_sets['C3'])

    def testRemoveCondition(self):
        cs = ConditionSet(name='condition_set', data=self.table, setop='AND')
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        cs.add_condition(cc)
        cc.add_category('C1')
        self.assertItemsEqual(cs.reference, self.fake_sets['C1'])
        cs.remove_condition(cc)
        self.assertEqual(cs.reference, [])

    def testEnablingChanges(self):
        cs = ConditionSet(name='condition_set', data=self.table, setop='AND')
        cc = CategoricalCondition(data=self.table, attr='fake_cat')
        rc = RangeCondition(data=self.table, attr='Information')
        rc.set_range(0.5, relative=True)

        cs.add_condition(cc)
        cc.add_category('C1')
        self.assertItemsEqual(cs.reference, self.fake_sets['C1'])
        cc.disable()
        print cs.query, cs.reference
        self.assertItemsEqual(cs.reference, [])

        cs.add_condition(rc)
        self.assertItemsEqual(cs.reference, ['CA', 'NY'])
        rc.enable(False)
        cc.enable()
        self.assertItemsEqual(cs.reference, self.fake_sets['C1'])

        cc.toggle_category(['C1', 'C3'])
        rc.enable()
        self.assertItemsEqual(cs.reference, ['NY'])

        rc.set_range(0, 1, relative=True)
        self.assertItemsEqual(cs.reference, self.fake_sets['C3'])


    def testGrammar(self):
        cs = ConditionSet(name='condition_set', data=self.table, setop='AND')
        cc = CategoricalCondition(data=self.table, attr='fake_cat', name='catc')
        rc = RangeCondition(data=self.table, attr='Information', name='rangec')
        ac = AttributeCondition(data=self.table, name='attrc')
        cs.add_condition(cc)
        cs.add_condition(rc)
        cs.add_condition(ac)

        print cs.grammar
        self.maxDiff = None
        self.assertDictEqual(cs.grammar, {'setop': 'AND',
                                      'conditions': [{'type': 'range',
                                                      'name': 'rangec',
                                                      'range': {'max': 492737.0,
                                                                'min': 3957.0,
                                                                'relative_min': 0.0,
                                                                'relative_max': 1.0},
                                                      'domain': {'max': 492737.0,
                                                                 'min': 3957.0},
                                                      'data': 'census',
                                                      'enabled': True,
                                                      'attr': 'Information'},
                                                     {'included_categories': [],
                                                      'excluded_categories': ['C3', 'C2', 'C1', 'C4'],
                                                      'name': 'catc',
                                                      'type': 'categorical',
                                                      'data': 'census',
                                                      'enabled': True,
                                                      'bins': None,
                                                      'attr': 'fake_cat'},
                                                      {'data': 'census',
                                                       'enabled': True,
                                                       'excluded_attributes': ['Information',
                                                                               'Other services (except public administration)',
                                                                               'Total for all sectors',
                                                                               'State',
                                                                               'Accommodation and food services',
                                                                               'Educational services',
                                                                               'Professional, scientific, and technical services',
                                                                               'Health care and social assistance',
                                                                               'Utilities',
                                                                               'Retail trade',
                                                                               'Construction',
                                                                               'Agriculture, forestry, fishing and hunting',
                                                                               'Arts, entertainment, and recreation',
                                                                               'Administrative and support and waste management and remediation services',
                                                                               'Finance and insurance',
                                                                               'Mining, quarrying, and oil and gas extraction',
                                                                               'Wholesale trade',
                                                                               'Management of companies and enterprises',
                                                                               'Transportation and warehousing',
                                                                               'Manufacturing',
                                                                               'Industries not classified',
                                                                               'Real estate and rental and leasing'],
                                                      'included_attributes': [],
                                                      'name': 'attrc',
                                                      'type': 'attribute'}],
                                      'data': 'census',
                                      'name': 'condition_set'})

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCreation']
    unittest.main()
