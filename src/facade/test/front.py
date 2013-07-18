# -*- coding: utf-8 -*-
'''
Created on 18/07/2013

@author: jmorales
'''
import unittest
from .. import front


class Foo(object):
    def __init__(self, name):
        self.name = name
        
    def echo(self, a):
        return a

    
class FooService(front.IService):

    def ping(self):
        return 'pong'

class Test(unittest.TestCase):

    def setUp(self):
        self.front = front.get_instance()
        
    def tearDown(self):
        self.front._services = {}

    def testRegister(self):
        foo_s = FooService('the_service')
        self.assertEqual(self.front._services['the_service'], foo_s)
        
        foo = Foo('foo')
        self.front.register(foo.name, foo)
        self.assertEqual(self.front._services[foo.name], foo)
        
        with self.assertRaises(ValueError):
            self.front.register(foo.name, foo)
            
    def testCall(self):
        name = 'the_service'
        FooService(name)
        res = self.front.call({'service':name, 'rpc': 'ping', 'args': {}})
        self.assertEqual('pong', res)
        
        foo = Foo('foo')
        self.front.register(foo.name, foo)
        res = self.front.call({'service':'foo', 'rpc': 'echo', 'args': {'a':'hello'}})
        self.assertEqual(res, 'hello')
        
    def testMagicCall(self):
        foo = Foo('foo')
        self.front.register(foo.name, foo)
        res = self.front.foo.echo('magic')
        self.assertEqual(res, 'magic')
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testRegister']
    unittest.main()