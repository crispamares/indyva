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
            self._channel = 'Achannel'

    def setUp(self):
        pass
    def tearDown(self):
        pass


    def testReactive(self):
        def myprint(change, channel):
            print '*** Event in %s, change type is %s' %(channel, change.type)
            
        s = Notifier.subscribe('Achannel/attr_a')
        s.on_event(myprint)
        
        a = self.A('paco')
        a.attr_a = 'pepe'
        
        print 'last thing'

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testReactive']
    unittest.main()