'''
Created on Sep 23, 2012

@author: crispamares
'''
import unittest
from table import Table, restrict_methods
import numpy as np
import pandas

class TestTable(unittest.TestCase):

    def setUp(self):
        self.table = Table(dict(col1=[1,2,3], col2=[4,5,6], col3=['a', 'b', 'c'])) 
        
    def test_decorator(self):
        @restrict_methods('max')
        class NArray(np.ndarray):
            pass
        @restrict_methods('max')
        class Row(pandas.Series):
            pass
        
        na = NArray([1,2,3])
        r = Row([1,2,3])
        r.max()
        with self.assertRaises(AttributeError):
            na.max()
        # The decorator do not work with pandas.Series
        #with self.assertRaises(AttributeError):
        #    r.max()

    def test_row(self):
        row = self.table.row(1)
        #self.assertEqual(str(row), "{'col2': 5, 'col3': 'b', 'col1': 2}")
        self.assertEqual(len(row), 3)
        self.assertListEqual(list(row), [2, 5, 'b'])
        self.assertListEqual([i for i in row], [2, 5, 'b'])
        self.assertListEqual(row.keys(), ['col1', 'col2', 'col3'])
        

    def test_rows(self):
        rows = self.table.rows([0,2])
        self.assertEqual(list(rows[1]), [3, 6, 'c'])

    def test_col(self):
        self.assertListEqual(self.table.col('col1'), [1,2,3])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()