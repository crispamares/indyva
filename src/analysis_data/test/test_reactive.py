'''
Created on Sep 23, 2012

@author: crispamares
'''
import unittest
from analysis_data.reactive import cached_property, ReactiveVariable, Observable


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
        
    def exampleObserver(self):
    
        class MyClass(object):
            """ A Class containing the observables length and width"""
            length = Observable('length')
            width = Observable('width')
    
            def __init__(self):
                self.length.setvalu(0)
                self.width.setvalu(0)
                
    
        class MyObserver(object):
            """An observer class. The initializer is passed an instance
               of 'myClass' and subscribes to length and width changes.
               This observer also itself contains an observable, l2"""
            
            l2 = Observable('l2')
    
            def __init__(self, name, observedObj):
                self.name = name
                self.subs1 = observedObj.length.subscribe(self.print_l)
                self.subs2 = observedObj.width.subscribe(self.print_w)
                
                """An observable can subscribe to an observable, in which case
                  a change will chain through both subscription lists.
                  Here l2's subscribers will be notified whenever observedObj.length
                  changes"""
                self.subs3 = observedObj.length.subscribe(self.l2)
    
            def print_w(self, value):
                print "%s Observed Width"%self.name, value
    
            def print_l(self, value):
                print "%s Observed Length"%self.name, value
                
            def cancel(self):
                """Cancels the instances current subscriptions. Setting self.subs1 to
                None removes the reference to the subscription object, causing it's 
                finalizer (__del__) method to be called."""
                self.subs1 = None
                self.subs2 = None
                self.subs3 = None
    
        def pl2(value):
            print "PL2 reports ", value
            if type(value) == type(3):
                raise ValueError("pl2 doesn't want ints.")
    
        def handlePl2Exceptions( ex ):
            print 'Handling pl2 exception:', ex, type(ex)
            return True     # true if handled, false if not
                
        area = MyClass()
        kent = MyObserver("Kent", area)
        billy = MyObserver("Billy", area)
        subscription = billy.l2.subscribe(pl2, handlePl2Exceptions)
    
        area.length = 6
        area.width = 4
        area.length = "Reddish"
    
        billy.subs1 = None
        print "Billy shouldn't report a length change to 5.15."
        area.length = 5.15      
        billy.cancel()
        print "Billy should no longer report"
        area.length = 7
        area.width = 3
        print "Areas values are ", area.length(), area.width()
    
        print "Deleting an object with observables having subscribers is ok"
        area = None
        area = MyClass()
        print "replaced area - no subscribers to this new instance"
        area.length = 5
        area.width ="Bluish"

        ## end of http://code.activestate.com/recipes/576979/ }}}
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCachedProperty']
    unittest.main()