# -*- coding: utf-8 -*-
'''
Created on 07/06/2013

@author: jmorales
'''
import unittest

import pandas as pn

from indyva.dataset import RSC_DIR
from indyva.IO.table_io import read_csv


class Test(unittest.TestCase):

    def setUp(self):
        self.df = pn.read_csv(RSC_DIR + '/census.csv')

    def testReadCsv(self):
        # Schema read from file
        table = read_csv("census_schema_file",
                         RSC_DIR + '/census.csv',
                         RSC_DIR + '/schema_census')
        self.assertEqual(table.row_count(), len(self.df))

        # Schema json string
        with open(RSC_DIR + '/schema_census') as f:
            schema = f.read()
        table = read_csv("census_schema_json", RSC_DIR + '/census.csv', schema)
        self.assertEqual(table.row_count(), len(self.df))

        # Schema infered
        table = read_csv("census_scheam_infered", RSC_DIR + '/census.csv')
        self.assertEqual(table.row_count(), len(self.df))


if __name__ == "__main__":
    unittest.main()
