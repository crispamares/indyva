# -*- coding: utf-8 -*-
'''
Created on 20/03/2013

@author: jmorales
'''
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import types

DataSetTypes = type("DataSetTypes", (), 
                    dict(TABLE='TABLE', NETWORK='NETWORK', TREE='TREE'))


class DataSetScheme:
    '''
    A DataSet Scheme is the definition of the related DataSet. Inside the 
    scheme at least are defined the DataSetType, and Indexes 
    '''
    __metaclass__ = ABCMeta

    _dataset_type = None    # DataSetType
    _indexes = tuple()
    
    @abstractmethod
    def __init__(self, indexes):        
        if type(indexes) == types.StringTypes:
            self._indexes = tuple([indexes])
        else:
            self._indexes = tuple(indexes)
    
    @property
    def dataset_type(self): 
        '''The dataset type. Currently the suported types are Table, Network 
        and Tree'''
        return self._dataset_type
        
    @property
    def indexes(self):
        '''Is a list with the name of the Attributes that are used as indexes'''
        return self._indexes
    
class TableScheme(DataSetScheme):
    def __init__(self, attributes, indexes):
        super(DataSetScheme, self).__init__(indexes)
        
        self._dataset_type = DataSetTypes.TABLE
        self._attributes = OrderedDict(attributes)
                
    @property
    def attributes(self):
        '''This is an OrededDict with the form - name:AttributeScheme'''
        return self._attributes
    