# -*- coding: utf-8 -*-
'''
Created on 04/09/2014

:author: Juan Morales
'''
import unittest

from indyva.dataset.shared_object import SharedObject, VersionError


class Test(unittest.TestCase):

    def callback(self, topic, msg):
        print topic, msg
        self.callback_executed = True

    def setUp(self):
        self.callback_executed = False

    def testCreation(self):
        so = SharedObject('SO1', {'a':42})
        self.assertIsInstance(so, SharedObject)

        so2 = SharedObject('SO2', [42,24])
        self.assertIsInstance(so2, SharedObject)

        with self.assertRaises(ValueError):
            SharedObject('SO3', 42)

    def testPull(self):
        so = SharedObject('SO1', {'a':42})
        data, version = so.pull()

        self.assertEqual(data, {'a':42})

    def testPush(self):
        so = SharedObject('SO1', {'a':42})

        data1, version1 = so.pull()
        data1['b'] = 24
        _, version2 = so.push(data1, version1)
        self.assertEqual(so._data, {'a':42, 'b': 24})

        data2, version2_again = so.pull()
        self.assertEqual(version2_again, version2)

        with self.assertRaises(VersionError):
            so.push([42], version1)

        so.push([42], version2)
        self.assertEqual(so._data, [42])

    def testEvents(self):
        so = SharedObject('SO1', {'a':42})
        so.subscribe('change', self.callback)

        data1, version1 = so.pull()
        data1['b'] = 24
        so.push(data1, version1)

        self.assertTrue(self.callback_executed)

if __name__ == "__main__":
    unittest.main()
