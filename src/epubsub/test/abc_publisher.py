# -*- coding: utf-8 -*-
'''
Created on 12/07/2013

@author: jmorales
'''
import unittest
from .. import abc_publisher
from .. import bus

class MyPublisher(abc_publisher.IPublisher):
    
    @abc_publisher.pub_result('hello')
    def world(self):
        return 'world'

class Test(unittest.TestCase):


    def testDecorator(self):
        def echo(topic, msg):
            print 'destination:', msg
        p = MyPublisher(bus.Bus(), ['hello'])
        p.subscribe('hello', echo)
        print p.world()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDecorator']
    unittest.main()