# -*- coding: utf-8 -*-
'''
Created on 17/07/2013

@author: jmorales
'''

class Endpoint(object):
    '''
    This class exposes the Front to remote clients over ZeroMQ transport layer
    
    It is also integrated with the event loop
    '''

    def __init__(self):
        '''
        Constructor
        '''
        