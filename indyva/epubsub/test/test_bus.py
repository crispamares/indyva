# -*- coding: utf-8 -*-
'''
Created on 06/06/2013

@author: jmorales
'''

import unittest

from indyva.epubsub import bus


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
        self.bus = bus.Bus()

    def tearDown(self):
        self.bus.close("topicA")
        self.bus.close("topicB")
        self.bus.close("topicC")

    def testSimpleTopic(self):
        self.bus.subscribe("topicA", self.a.sumAB)
        self.bus.publish("topicA", {'a':2,'b':5})
        self.assertEqual(self.a.result, 7)

    def testMultiSubscribers(self):
        self.a2 = self.A()
        self.bus.subscribe("topicA", self.a.sumAB)
        self.bus.subscribe("topicA", self.a2.sumAB)
        self.bus.publish("topicA", {'a':2,'b':5})
        self.assertEqual(self.a.result, 7)
        self.assertEqual(self.a2.result, 7)

    def testLostMsgs(self):
        self.a2 = self.A()
        self.bus.subscribe("topicA", self.a.sumAcum)
        self.bus.publish("topicA", {'a':2})
        self.bus.subscribe("topicA", self.a2.sumAcum)
        self.bus.publish("topicA", {'a':3})
        self.assertEqual(self.a.result, 5)
        self.assertEqual(self.a2.result, 3)

    def testSubscribeOnce(self):
        self.a2 = self.A()
        self.bus.subscribe("topicA", self.a2.sumAcum)
        self.bus.subscribe_once("topicA", self.a.sumAcum)
        self.bus.publish("topicA", {'a':2})
        self.bus.publish("topicA", {'a':3})
        self.assertEqual(self.a.result, 2)
        self.assertEqual(self.a2.result, 5)

    def testUnsubscribe(self):
        self.bus.subscribe("topicA", self.a.sumAB)
        self.bus.unsubscribe("topicA", self.a.sumAB)
        self.bus.publish("topicA", {'a':2,'b':5})
        self.assertEqual(self.a.result, 0)

        with self.assertRaises(KeyError):
            self.bus.unsubscribe("topicA", self.a.sumAB)
        with self.assertRaises(KeyError):
            self.bus.unsubscribe("topicB", self.a.sumAB)
        with self.assertRaises(KeyError):
            self.bus.unsubscribe("topicA", self.a.sumAcum)

    def testClose(self):
        self.a2 = self.A()
        self.bus.subscribe("topicA", self.a.sumAB)
        self.bus.subscribe("topicA", self.a2.sumAB)

        self.bus.close("topicA")
        self.bus.publish("topicA", {'a':2,'b':5})
        self.assertEqual(self.a.result, 0)
        self.assertEqual(self.a2.result, 0)

        self.bus.close("topicA")




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
