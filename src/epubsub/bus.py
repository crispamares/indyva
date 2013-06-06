# -*- coding: utf-8 -*-
'''
Created on 06/06/2013

@author: jmorales
'''
import hub

DEFAULT_PREFIX_TOPIC = ""

class Bus(object):
    '''
    Exposes the PubSub functionality of the Hub in a more convenient way
    '''

    def __init__(self, prefix=DEFAULT_PREFIX_TOPIC):
        '''
        @param prefix: This str is the prefix of all the pubsub topics of
         this bus 
        '''
        self._prefix = prefix
        self._hub = hub.get_instance()
        
    def __del__(self):
        pass