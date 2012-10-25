'''
Created on Oct 25, 2012

@author: crispamares
'''
import unittest
from analysis_data.reactive import Reactive, Notifier

class Test(unittest.TestCase):
    class A(object):
        __metaclass__ = Reactive
        
        def __init__(self, attr_a):
            self.attr_a = None
            self.channel = 'Achannel'

    def setUp(self):
        pass
    def tearDown(self):
        pass


    def testReactive(self):
        s = Notifier.subscribe('Achannel/attr_a')
        print s
        a = self.A('paco')
        a.attr_a = 'pepe'
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testReactive']
    unittest.main()