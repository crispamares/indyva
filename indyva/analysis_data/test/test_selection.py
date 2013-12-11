'''
Created on Sep 28, 2012

@author: crispamares
'''
import unittest
from analysis_data.selection import Selection
import pandas as pn

class Test(unittest.TestCase):


    def setUp(self):
        self.table = pn.DataFrame(pn.np.random.random([4,2]), columns=['a','b'])
        self.s1 = Selection(self.table)
        self.s2 = Selection(self.table, [])
        self.i1 = pn.Index([0,1,3])
        self.i2 = pn.Index([2])
        pass

    def tearDown(self):
        pass

    def test_replace(self):
        self.s1.replace(self.i1)
        self.assertEqual(self.s1, Selection(self.table, self.i1))

    def test_add(self):
        self.s2.union(self.i1)
        self.assertEqual(self.s2, Selection(self.table, self.i1))
        self.s2.union(self.i2)
        self.assertEqual(self.s2, Selection(self.table))
        self.s2.union(self.i1)
        self.assertEqual(self.s2, Selection(self.table))
        
    def test_substract(self):
        self.s1.substract(self.i2)
        self.assertEqual(self.s1, Selection(self.table, self.i1))
        self.s1.substract(self.i2)
        self.assertEqual(self.s1, Selection(self.table, self.i1))
        self.s1.substract(self.i1)
        self.assertEqual(self.s1,self.s2)
        
    def test_toggle(self):
        self.s1.toggle()
        self.assertEqual(self.s1,self.s2)
        
    def test_intersect(self):
        self.s1.intersect(self.i1)
        self.assertEqual(self.s1, Selection(self.table, self.i1))
        self.s1.intersect(pn.Index([2,3]))
        self.assertEqual(self.s1, Selection(self.table, [3]))
        
    def test_all(self):
        selec = Selection(self.table, [1,2])
        selec.replace([0,2])
        selec.union([3])
        selec.substract([0])
        selec.toggle()
        self.assertEqual(selec, Selection(self.table, [0,1]))

    def test_selected(self):
        selec = Selection(self.table, [1,2])
        t = selec.selected()
        self.assert_(pn.np.allclose(t, self.table.ix[[1,2]]))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test']
    unittest.main()