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

    def _subscribe(self, topic, destination, only_once=False, group_id=None):
        ''' TODO: publish new subscriptions and new topics through meta topic'''
        if not self._subscriptions.has_key(topic):
            self._subscriptions[topic] = {}
        topic_destinations = self._subscriptions[topic]
        
        subscription_info = {}
        if only_once: subscription_info['only_once'] = True
        if group_id is not None: subscription_info['group_id'] = group_id 
        
        topic_destinations[destination] = subscription_info
              
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
        
    def _unsibscribe_by_group_id(self, group_id):
        for topic, destinations in self._subscriptions.items(): 
            for destination, subscription_info in destinations.items():
                if subscription_info.get('group_id', None) == group_id:
                    self.unsubscribe(topic, destination)
        
    def publish(self, topic, msg):
        ''' TODO: publish No one subscribe through meta topic'''
        destinations = self._subscriptions.get(topic, {})
        for destination, subscription_info in destinations.items():
            self._send_msg(topic, destination, msg)
            if subscription_info.get('only_once', False):
                self.unsubscribe(topic, destination)
        
    def _send_msg(self, topic, destination, msg):
        destination(topic, msg)


def _singleton():
    hub = Hub()
    while True:
        yield hub
        
def get_instance():
    return _singleton().next()
