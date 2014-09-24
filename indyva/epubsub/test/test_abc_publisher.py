# -*- coding: utf-8 -*-
'''
Created on 12/07/2013

@author: jmorales
'''
import unittest

from indyva.epubsub import abc_publisher
from indyva.epubsub import bus


class MyPublisher(abc_publisher.IPublisher):

    @abc_publisher.pub_result('hello')
    def by_pass(self, a):
        return a


class Test(unittest.TestCase):

    def testDecorator(self):

        class S(object):
            def __init__(self):
                self.callback_executed = False

            def throw(self, topic, msg):
                self.callback_executed = True
                raise RuntimeError(msg)

        p = MyPublisher(bus.Bus(), ['hello'])
        s = S()
        p.subscribe('hello', s.throw)


        s.callback_executed = False
        with self.assertRaises(RuntimeError):
            self.assertEqual(p.by_pass(1), 1)
        self.assertEqual(s.callback_executed, True)

        s.callback_executed = False
        p.by_pass(2, pub_options={'silent':True})
        self.assertEqual(s.callback_executed, False)

if __name__ == "__main__":
    unittest.main()
