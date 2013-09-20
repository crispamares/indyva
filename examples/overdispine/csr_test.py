# -*- coding: utf-8 -*-
'''
Created on 20/09/2013

@author: jmorales
'''

class CSRTest(object):
    '''
    Spawn a R task that checks CSR null hypothesis
    '''
    def __init__(self, selection=None):
        self.selection =  selection
        
        #TODO: This class needs to have derived columns functionality in tables
        #TODO: Actually needs remote derived columns  
