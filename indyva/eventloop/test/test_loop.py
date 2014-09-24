'''
Created on Oct 17, 2013

@author: crispamares
'''
import unittest

import time

from indyva.eventloop import ZMQLoop, QtLoop


class TestLoopBase(object):

    class A(object):
        acum = 0
        def inc(self):
            self.acum += 1

    def setUp(self):
        self.a = self.A()

    def tearDown(self):
        self.loop.stop()
        self.loop

    def testPeriodics(self):
        print 'START'
        self.loop.add_periodic_callback(self.a.inc, 10, 'inc', start=True)
        self.loop.add_periodic_callback(self.loop.stop, 51, 'stop', start=True)

        self.loop.start()
        self.assertEqual(self.a.acum , 5)
        print 'STOP'

    def testReStartPeriodics(self):
        '''
        The periodic should not reprogram the periodic callback in the
        start_periodic method if the periodic is already programmed.
        '''
        print 'START'
        self.loop.add_periodic_callback(self.a.inc, 10, 'inc')
        self.loop.add_periodic_callback(self.loop.stop, 51, 'stop')

        self.loop.start_periodic('inc')
        self.loop.start_periodic('stop')

        time.sleep(0.010)
        self.loop.start_periodic('inc')

        self.loop.start()
        self.assertEqual(self.a.acum , 5)
        print 'STOP'

    def testNoStart(self):
        '''
        This test could be confusing. The callback is not executed not because
        the timers of the periodics are not set, but because there is no context
        change. The sleep here freeze the wole process so there is no chance
        of executing the events. No loop, means no event processing.
        '''
        print 'START'
        self.loop.add_periodic_callback(self.a.inc, 10, 'inc')
        self.loop.start_periodic('inc')

        time.sleep(0.05)
        # EXPLICIT NO START --> self.loop.start()
        self.assertEqual(self.a.acum , 0)
        print 'STOP'

    def testDeferedStart(self):
        '''
        This tests that the periodic fires that can not be programmed at time
        are no gonna fire anymore. The accumulator should be 19, but the first 9
        executions are missed because of the sleep
        '''
        print 'START'
        self.loop.add_periodic_callback(self.a.inc, 10, 'inc')
        self.loop.add_periodic_callback(self.loop.stop, 195, 'stop')
        self.loop.start_periodic('inc')
        self.loop.start_periodic('stop')

        time.sleep(0.1)
        self.loop.start()
        self.assertEqual(self.a.acum , 10) # instead of 19
        print 'STOP'

class TestZMQLoop(TestLoopBase, unittest.TestCase):

    def setUp(self):
        self.loop = ZMQLoop()
        self.loop.loop.initialize()
        super(TestZMQLoop, self).setUp()



class TestQtLoop(TestLoopBase, unittest.TestCase):


    def setUp(self):
        self.loop = QtLoop()
        super(TestQtLoop, self).setUp()


    @classmethod
    def setUpClass(cls):
        import PyQt4
        cls.app = PyQt4.QtGui.QApplication([])
        super(TestQtLoop, cls).setUpClass()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCreation']
    unittest.main()
