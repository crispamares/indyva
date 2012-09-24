'''
Created on Sep 23, 2012

@author: crispamares
'''
import unittest
from reactive import cached_property, ReactiveVariable


class fooA(object):
    def __init__(self):
        self.foolist = []
    
    @cached_property
    def prop_a(self):
        self.foolist.append('val')
        return 'val'

    def calc_with_prop_a(self):
        return self.prop_a + ' expanded'

class fooB(object):
    def __init__(self):
        fooB.prop_b = ReactiveVariable(self, 'prop_b', 34)

            
class Test(unittest.TestCase):

    def setUp(self):
        self.a = fooA()
        self.b1 = fooB()
        self.b2 = fooB()

    def tearDown(self):
        pass

    def testCachedProperty_compute(self):
        self.assertEqual(self.a.prop_a, 'val')
        
    def testCachedProperty_cache(self):
        self.assertEqual(len(self.a.foolist), 0)
        self.assertEqual(self.a.prop_a, 'val')
        self.assertEqual(len(self.a.foolist), 1)
        self.assertEqual(self.a.prop_a, 'val')
        self.assertEqual(len(self.a.foolist), 1)

    def testCachedProperty_interal_access(self):
        self.assertEqual(self.a.calc_with_prop_a(), 'val expanded')

    def testObservableProperty(self):
        self.assertEqual(self.b1.prop_b, 34)
        self.b1.prop_b = 56
        self.assertEqual(self.b1.prop_b, 56)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCachedProperty']
    unittest.main()