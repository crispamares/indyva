import unittest

import pandas as pd
import json
from collections import OrderedDict


from indyva.core import names
from indyva.core.grava import Root

from indyva.dataset.table import Table
from indyva.dataset.shared_object import SharedObject
from indyva.dataset import RSC_DIR
from indyva.dynamics.condition import (CategoricalCondition, RangeCondition,
                                       QueryCondition, AttributeCondition)
from indyva.dynamics.condition_set import ConditionSet
from indyva.dynamics.dselect import DynSelect
from indyva.dynamics.dfilter import DynFilter


class RootTest(unittest.TestCase):

    def setUp(self):
        self.root = Root("root")
        self.root2 = Root("root2")

        self.createTable()
        self.createConditions()
        self.createDynamics()
        self.createSharedObject()

    def tearDown(self):
        names.clear()

    def createTable(self):
        self.df = pd.read_csv(RSC_DIR + '/census.csv')
        with open(RSC_DIR + '/schema_census') as f:
            schema = json.loads(f.read())

        self.schema = OrderedDict(attributes=schema['attributes'], index=schema['index'])
        self.table = Table('census', self.schema).data(self.df)

        self.table.add_column('fake_cat', 'CATEGORICAL')
        items = self.table.index_items()
        fake_cat = ['C1','C2','C3','C4']
        for i, item in enumerate(items):
            self.table.update({'State':item}, {'$set': {'fake_cat': fake_cat[i % 4]}})

        self.root.add_dataset(self.table)

    def createConditions(self):
        self.categorical_condition = CategoricalCondition(data=self.table, attr='fake_cat')
        self.range_condition = RangeCondition(data=self.table, attr='Information',
                                              range=dict(min=250000, max=500000))
        self.query_condition = QueryCondition(data=self.table, query={'State':'NY'})
        self.attribute_condition = AttributeCondition(data=self.table, attributes=['Information'])

        self.consition_set = ConditionSet(name='condition_set', data=self.table, setop='AND')
        self.consition_set.add_condition(self.categorical_condition)
        self.consition_set.add_condition(self.range_condition)
        self.consition_set.add_condition(self.query_condition)
        self.consition_set.add_condition(self.attribute_condition)

        self.root.add_condition(self.categorical_condition)
        self.root.add_condition(self.range_condition)
        self.root.add_condition(self.query_condition)
        self.root.add_condition(self.attribute_condition)

    def createDynamics(self):
        self.filter1 = DynFilter("filer1", self.table)
        self.filter1.add_condition(self.range_condition)

        self.filter2 = DynFilter("filer2", self.table)
        self.filter2.add_condition(self.query_condition)
        self.filter2.add_condition(self.attribute_condition)

        self.selection = DynSelect("selection", self.table)
        self.selection.add_condition(self.categorical_condition)

        self.root.add_dynamic(self.filter1)
        self.root.add_dynamic(self.filter2)
        self.root.add_dynamic(self.selection)

    def createSharedObject(self):
        self.shared_object = SharedObject("shared_object", {'a':42, 'b':[1,2,3,4]})

        self.root.add_dataset(self.shared_object)

    def testCreation(self):
        from pprint import pprint
        grammar = self.root.grammar
        pprint(grammar)

        names.clear()
        objects = Root.build(grammar)

        self.assertIn(self.table.name, objects)
        self.assertIn(self.attribute_condition.name, objects)
        self.assertIn(self.categorical_condition.name, objects)
        self.assertIn(self.range_condition.name, objects)
        self.assertIn(self.query_condition.name, objects)
        self.assertIn(self.filter1.name, objects)
        self.assertIn(self.filter2.name, objects)
        self.assertIn(self.selection.name, objects)
        self.assertIn(self.shared_object.name, objects)

        self.assertIsInstance(self.table, Table)
        self.assertIsInstance(self.attribute_condition, AttributeCondition)
        self.assertIsInstance(self.categorical_condition, CategoricalCondition)
        self.assertIsInstance(self.range_condition, RangeCondition)
        self.assertIsInstance(self.query_condition, QueryCondition)
        self.assertIsInstance(self.filter1, DynFilter)
        self.assertIsInstance(self.filter2, DynFilter)
        self.assertIsInstance(self.selection, DynSelect)
        self.assertIsInstance(self.shared_object, SharedObject)
