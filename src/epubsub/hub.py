# -*- coding: utf-8 -*-
'''
Created on 06/06/2013

@author: jmorales
'''

class Hub(object):
    '''
    For common uses the Bus is preferred 
    
    The broker of the pubsub system. Handles the subscriptions table.
    '''

    def __init__(self):
        self._subscriptions = {}

    def _subscribe(self, topic, destination, only_once):
        ''' TODO: publish new subscriptions and new topics through meta topic'''
        if not self._subscriptions.has_key(topic):
            self._subscriptions[topic] = {}
        topic_destinations = self._subscriptions[topic]
        topic_destinations[destination] = only_once
              
    def subscribe(self, topic, destination):
        self._subscribe(topic, destination, only_once=False)
        
    def subscribe_once(self, topic, destination):
        self._subscribe(topic, destination, only_once=True)
        
    def unsubscribe(self, topic, destination):
        self._subscriptions[topic].pop(destination)
    
    def close(self, topic):
        '''Removes all the subscriptions to a topic. 
           No error trying to close unexpected topic
           @param topic: str
        '''
        self._subscriptions.pop(topic, None) 
        
    def publish(self, topic, msg):
        ''' TODO: publish No one subscribe through meta topic'''
        destinations = self._subscriptions.get(topic, {})
        for destination, only_once in destinations.items():
            self._send_msg(topic, destination, msg)
            if only_once:
                self.unsubscribe(topic, destination)
        
    def _send_msg(self, topic, destination, msg):
        destination(topic, msg)

_instance = None
def get_instance():
    if _instance is None:
        _instance = Hub()
    return _instance