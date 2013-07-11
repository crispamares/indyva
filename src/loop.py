# -*- coding: utf-8 -*-
'''
Created on 11/07/2013

@author: jmorales
'''

import time

FREQ = 0.000001

class Loop(object):
    '''
    The event loop sorts and prioritizes the reactions to the events. 
    '''

    def __init__(self):
        '''
        
        '''
        
    def run(self):
        while True:
            time.sleep(FREQ)
            
if __name__ == '__main__':
    loop = Loop()
    loop.run()        