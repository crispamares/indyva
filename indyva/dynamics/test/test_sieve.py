'''
Created on Oct 3, 2013

@author: crispamares
'''
import unittest

import pandas as pd
import json
from collections import OrderedDict

from indyva.dataset import RSC_DIR
from indyva.dataset.table import Table
from indyva.dynamics.sieve import (ItemImplicitSieve, AttributeImplicitSieve,
                             ItemExplicitSieve, SieveSet)
from indyva.core import names

class TestItemImplicitSieve(unittest.TestCase):

    def setUp(self):
        self.df = pd.read_csv(RSC_DIR+'/census.csv')
        with open(RSC_DIR+'/schema_census') as f:
            schema = json.loads(f.read())

        self.schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])
        self.table = Table('census', self.schema).data(self.df)

    def tearDown(self):
        names.clear()

    def testCreate(self):
        s = ItemImplicitSieve(self.table, [])
        self.assertEqual(s.index , set([]))

    def testDomain(self):
        s = ItemImplicitSieve(self.table, [])
        self.assertSetEqual(s.domain , set(self.table.index_items()))

    def testIndex(self):
        s = ItemImplicitSieve(self.table, [])
        self.assertEqual(s.index , set([]))
        s.index = ['DC', 'NY']
        self.assertEqual(s.index , set(['DC', 'NY']))

    def testQuery(self):
        s = ItemImplicitSieve(self.table, ['DC', 'NY'])
        self.assertEqual(s.query , {self.table.index : {'$in': ['NY', 'DC']}})

    def testUnion(self):
        s = ItemImplicitSieve(self.table, [])
        s.union(['DC'])
        s.union(['NY'])
        self.assertEqual(s.query , {self.table.index : {'$in': ['NY', 'DC']}})
        s.union(['DC', 'NY'])
        self.assertEqual(s.query , {self.table.index : {'$in': ['NY', 'DC']}})

    def testSubstract(self):
        s = ItemImplicitSieve(self.table, [])
        s.substract(['DC'])
        self.assertEqual(s.index , set([]))
        s.index = ['DC', 'NY']
        s.substract(['DC'])
        self.assertEqual(s.index , set(['NY']))

    def testToggle(self):
        s = ItemImplicitSieve(self.table, [])
        s.index = s.domain.difference(['NY', 'DC'])
        s.toggle()
        self.assertEqual(s.index , set(['NY', 'DC']))

    def testIntersect(self):
        s = ItemImplicitSieve(self.table, ['NY', 'DC', 'WA'])
        s.intersect(['NY', 'DC'])
        self.assertEqual(s.index , set(['NY', 'DC']))



class TestAttributeImplicitSieve(unittest.TestCase):

    def setUp(self):
        self.df = pd.read_csv(RSC_DIR+'/census.csv')
        with open(RSC_DIR+'/schema_census') as f:
            schema = json.loads(f.read())

        self.schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])
        self.table = Table('census', self.schema).data(self.df)

    def tearDown(self):
        names.clear()

    def testDomain(self):
        s = AttributeImplicitSieve(self.table, [])
        self.assertSetEqual(s.domain , set(self.table.column_names()))

    def testProjection(self):
        s = AttributeImplicitSieve(self.table, [])
        self.assertEqual(s.projection , {})
        s.index = ['Information', 'State']
        self.assertEqual(s.projection ,  {u'Information': True, u'State': True})



class TestItemExplicitSieve(unittest.TestCase):

    def setUp(self):
        self.df = pd.read_csv(RSC_DIR+'/census.csv')
        with open(RSC_DIR+'/schema_census') as f:
            schema = json.loads(f.read())

        self.schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])
        self.table = Table('census', self.schema).data(self.df)

    def tearDown(self):
        names.clear()

    def testCreate(self):
        s = ItemExplicitSieve(self.table, {})
        self.assertEqual(s.query , {})

    def testDomain(self):
        s = ItemExplicitSieve(self.table, {})
        self.assertSetEqual(s.domain , set(self.table.index_items()))

    def testIndex(self):
        s = ItemExplicitSieve(self.table, {})
        self.assertEqual(s.index , set(self.table.index_items()))
        s.query = {'Information':  {'$gt': 200000}}
        self.assertEqual(s.index , set(['CA', 'TX', 'NY']))

    def testQuery(self):
        s = ItemExplicitSieve(self.table, {'Information':  {'$gt': 200000}})
        self.assertEqual(s.query , {'Information':  {'$gt': 200000}})

    def testUnion(self):
        s = ItemExplicitSieve(self.table, {'Information':  {'$gt': 200000}})
        s.union({'State' : {'$in': ['NY', 'DC']}})
        self.assertEqual(s.query , {'$or': [{'Information': {'$gt': 200000}},
                                            {'State': {'$in': ['NY', 'DC']}}]})
        self.assertEqual(s.index , set(['CA', 'TX', 'NY', 'DC']))

    def testSubstract(self):
        s = ItemExplicitSieve(self.table, {'Information':  {'$gt': 200000}})
        s.substract({'State' : {'$in': ['NY', 'DC']}})
        self.assertEqual(s.query , {'$and': [{'Information': {'$gt': 200000}},
                                             {'$nor': [{'State': {'$in': ['NY', 'DC']}}]}]})
        self.assertEqual(s.index , set(['CA', 'TX']))

    def testToggle(self):
        s = ItemExplicitSieve(self.table, {'Information':  {'$lt': 200000}})
        s.toggle()
        self.assertEqual(s.query , {'$nor': [{'Information': {'$lt': 200000}}]})
        self.assertEqual(s.index , set(['CA', 'TX', 'NY']))

    def testIntersect(self):
        s = ItemExplicitSieve(self.table, {'Information':  {'$gt': 200000}})
        s.intersect({'State' : {'$in': ['NY', 'DC']}})
        self.assertEqual(s.index , set(['NY']))
        self.assertEqual(s.query , {'$and': [{'Information': {'$gt': 200000}},
                                             {'State': {'$in': ['NY', 'DC']}}]})


class TestSieveSet(unittest.TestCase):

    def setUp(self):
        self.df = pd.read_csv(RSC_DIR+'/census.csv')
        with open(RSC_DIR+'/schema_census') as f:
            schema = json.loads(f.read())

        self.schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])
        self.table = Table('census', self.schema).data(self.df)
        self.impls = ItemImplicitSieve(self.table, ['DC', 'NY'])
        self.expls = ItemExplicitSieve(self.table, {'Information': {'$gt': 200000}})
        self.attrs = AttributeImplicitSieve(self.table, ['Information', 'State'])

    def tearDown(self):
        names.clear()

    def testCreate(self):
        ss = SieveSet(self.table)
        self.assertEqual(ss.query,  {u'State': {'$in': []}})
        self.assertEqual(ss.projection, {})
        self.assertEqual(ss.reference, set([]))

    def testAddsieveWithAND(self):
        ss = SieveSet(self.table)

        ss.add_sieve(self.impls)
        self.assertEqual(ss.query,  {u'State': {'$in': ['NY', 'DC']}})
        self.assertEqual(ss.projection, {})
        self.assertEqual(ss.reference, set(['DC', 'NY']))

        ss.add_sieve(self.expls)
        self.assertEqual(ss.query,  {'$and': [{'Information': {'$gt': 200000}},
                                              {u'State': {'$in': ['NY', 'DC']}}]})
        self.assertEqual(ss.projection, {})
        self.assertEqual(ss.reference, set(['NY']))

        ss.add_sieve(self.attrs)
        self.assertEqual(ss.query,  {'$and': [{'Information': {'$gt': 200000}},
                                              {u'State': {'$in': ['NY', 'DC']}}]})
        self.assertEqual(ss.projection, {u'Information': True, u'State': True})
        self.assertEqual(ss.reference, set(['NY']))

    def testSetSieveWithOR(self):
        ss = SieveSet(self.table, 'OR')

        ss.set_sieve('implicit', self.impls)
        self.assertEqual(ss.query,  {u'State': {'$in': ['NY', 'DC']}})
        self.assertEqual(ss.projection, {})
        self.assertEqual(ss.reference, set(['DC', 'NY']))

        ss.set_sieve('explicit', self.expls)
        self.assertEqual(ss.query,  {'$or': [{'Information': {'$gt': 200000}},
                                              {u'State': {'$in': ['NY', 'DC']}}]})
        self.assertEqual(ss.projection, {})
        self.assertEqual(ss.reference, set(['CA', 'TX', 'NY', 'DC']))

        ss.set_sieve('attributes', self.attrs)
        self.assertEqual(ss.query,  {'$or': [{'Information': {'$gt': 200000}},
                                              {u'State': {'$in': ['NY', 'DC']}}]})
        self.assertEqual(ss.projection, {u'Information': True, u'State': True})
        self.assertEqual(ss.reference, set(['CA', 'TX', 'NY', 'DC']))


    def testRemoveWithOR(self):
        ss = SieveSet(self.table, 'OR')

        ss.set_sieve('implicit', self.impls)
        ss.set_sieve('explicit', self.expls)
        ss.set_sieve('attributes', self.attrs)

        self.assertEqual(ss.query,  {'$or': [{'Information': {'$gt': 200000}},
                                              {u'State': {'$in': ['NY', 'DC']}}]})
        self.assertEqual(ss.projection, {u'Information': True, u'State': True})
        self.assertEqual(ss.reference, set(['CA', 'TX', 'NY', 'DC']))

        ss.remove_sieve('attributes')
        self.assertEqual(ss.query,  {'$or': [{'Information': {'$gt': 200000}},
                                              {u'State': {'$in': ['NY', 'DC']}}]})
        self.assertEqual(ss.projection, {})
        self.assertEqual(ss.reference, set(['CA', 'TX', 'NY', 'DC']))

        ss.remove_sieve('explicit')
        self.assertEqual(ss.query,  {u'State': {'$in': ['NY', 'DC']}})
        self.assertEqual(ss.projection, {})
        self.assertEqual(ss.reference, set(['DC', 'NY']))





if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testItemImplicitSieve']
    unittest.main()
