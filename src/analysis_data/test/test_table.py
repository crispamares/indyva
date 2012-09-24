'''
Created on Sep 23, 2012

@author: crispamares
'''
import unittest
from table import Table

class TestTable(unittest.TestCase):

    def setUp(self):
        self.table = Table(dict(col1=[1,2,3], col2=[4,5,6], col3=['a', 'b', 'c'])) 

    def test_rows(self):
        row = self.table.rows([0,2])
        #self.assertEqual(str(row), "[[1, 4, 'a'], [3, 6, 'c']]", 'Error Table.rows %s' % row)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()