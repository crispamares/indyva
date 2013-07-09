'''
Created on Jun 26, 2013

@author: crispamares
'''
from bus import Bus
from abc import ABCMeta

'''@@var TESTDESCRIPTION: If True every subscription is asserted to be
the list of topics'''
TESTSUBSCRIPTION = True

class IPublisher(object):
    '''
    This class is useful for publishers that want to provide
    and an easy way to subscribe to it own topics. 
    
    Hides the bus and hub classes for the subscribers
    '''
    
    __metaclass__ = ABCMeta

    def __init__(self, bus, topics=[]):
        '''
        @param bus: epubsub.bus.Bus
        '''
        self._bus = bus
        self._topics = topics
        
    def subscribe(self, topic, destination):
        if TESTSUBSCRIPTION:
            assert topic in self._topics
        self._bus.subscribe(topic, destination)
        
    def subscribe_once(self, topic, destination):
        if TESTSUBSCRIPTION:
            assert topic in self._topics
        self._bus.subscribe_once(topic, destination)
        
    def unsubscribe(self, topic, destination):
        if TESTSUBSCRIPTION:
            assert topic in self._topics        
        self._bus.unsubscribe(topic, destination)
    