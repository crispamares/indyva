# -*- coding: utf-8 -*-
'''
Created on 06/06/2013

@author: jmorales
'''
import unittest
from .. import hub 

class Test(unittest.TestCase):
    class A(object):
        def __init__(self):
            self.result = 0
        def sumAB(self, topic, msg):
            self.result = msg['a'] + msg['b']
        def sumAcum(self, topic, msg):
            self.result += msg['a']

    def setUp(self):
        self.a = self.A()
        self.hub = hub.Hub()

    def testSimpleTopic(self):
        self.hub.subscribe("topicA", self.a.sumAB)
        self.hub.publish("topicA", {'a':2,'b':5})
        self.assertEqual(self.a.result, 7)
    
    def testMultiSubscribers(self):
        self.a2 = self.A()
        self.hub.subscribe("topicA", self.a.sumAB)
        self.hub.subscribe("topicA", self.a2.sumAB)
        self.hub.publish("topicA", {'a':2,'b':5})
        self.assertEqual(self.a.result, 7)
        self.assertEqual(self.a2.result, 7)

    def testLostMsgs(self):
        self.a2 = self.A()
        self.hub.subscribe("topicA", self.a.sumAcum)
        self.hub.publish("topicA", {'a':2})
        self.hub.subscribe("topicA", self.a2.sumAcum)
        self.hub.publish("topicA", {'a':3})
        self.assertEqual(self.a.result, 5)
        self.assertEqual(self.a2.result, 3)

    def testSubscribeOnce(self):
        self.a2 = self.A()
        self.hub.subscribe("topicA", self.a2.sumAcum)
        self.hub.subscribe_once("topicA", self.a.sumAcum)
        self.hub.publish("topicA", {'a':2})
        self.hub.publish("topicA", {'a':3})
        self.assertEqual(self.a.result, 2)
        self.assertEqual(self.a2.result, 5)  

    def testUnsubscribe(self):
        self.hub.subscribe("topicA", self.a.sumAB)
        self.hub.unsubscribe("topicA", self.a.sumAB)
        self.hub.publish("topicA", {'a':2,'b':5})
        self.assertEqual(self.a.result, 0)
        
        with self.assertRaises(KeyError):
            self.hub.unsubscribe("topicA", self.a.sumAB)
        with self.assertRaises(KeyError):
            self.hub.unsubscribe("topicB", self.a.sumAB)
        with self.assertRaises(KeyError):
            self.hub.unsubscribe("topicA", self.a.sumAcum)
    
    def testClose(self):
        self.a2 = self.A()
        self.hub.subscribe("topicA", self.a.sumAB)
        self.hub.subscribe("topicA", self.a2.sumAB)

        self.hub.close("topicA")
        self.hub.publish("topicA", {'a':2,'b':5})
        self.assertEqual(self.a.result, 0)
        self.assertEqual(self.a2.result, 0)
        
        self.hub.close("topicA")
        
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()