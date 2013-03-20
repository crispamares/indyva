# -*- coding: utf-8 -*-
'''
Created on 20/03/2013

@author: jmorales
'''

from abc import ABCMeta, abstractmethod

class ITable:
    '''
    This class is a DataSet Type, an abstraction of Tabluar Data
    '''
    __metaclass__ = ABCMeta
    
    def __init__(self):
        '''
        Constructor
        '''
        