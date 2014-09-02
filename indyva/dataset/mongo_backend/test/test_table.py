'''
Created on 26/03/2013

@author: crispamares
'''
import unittest

import pandas as pn
import json
from collections import OrderedDict

from indyva.dataset.mongo_backend.table import MongoTable
from indyva.dataset import RSC_DIR


class Test(unittest.TestCase):

    def setUp(self):
        self.df = pn.read_csv(RSC_DIR + '/census.csv')
        with open(RSC_DIR + '/schema_census') as f:
            schema = json.loads(f.read())

        self.schema = OrderedDict(attributes=schema['attributes'],
                                  index=schema['index'])

    def testCreationAsList(self):
        data = []
        for i in range(len(self.df)):
            data.append(self.df.ix[i].to_dict())

        MongoTable('census', self.schema).data(data)

    def testCreationAsDataFrame(self):
        data = self.df
        MongoTable('census', self.schema).data(data)

    def testCreationWithoutSchema(self):
        MongoTable('census')

    def testGetData(self):
        table = MongoTable('census', self.schema).data(self.df)
        self.assertEqual(len(table.get_data()), len(self.df))

    def testGetViewData(self):
        table = MongoTable('census', self.schema).data(self.df)
        result = table.get_view_data([{'query':{'State':'DC'}}])
        self.assertEqual(result[0]['State'], 'DC')

    def testFindOne(self):
        table = MongoTable('census', self.schema).data(self.df)
        result = table.find_one(dict(query={'$or':[{'State': 'NY'},{'State': 'DC'}]}))
        self.assertIn(result['State'], ['DC','NY'])


if __name__ == "__main__":
    unittest.main()
