# -*- coding: utf-8 -*-
'''
Created on 20/03/2013

@author: jmorales
'''
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import types
from copy import copy

DataSetTypes = type("DataSetTypes", (), 
                    dict(TABLE='TABLE', NETWORK='NETWORK', TREE='TREE'))
AttributeTypes = type("AttributeTypes", (), 
                      dict(CATEGORICAL='CATEGORICAL', 
                           ORDINAL='ORDINAL',QUANTITATIVE='QUANTITATIVE'))


class DataSetScheme:
    '''
    A DataSet Scheme is the definition of the related DataSet. Inside the 
    scheme at least are defined the DataSetType, and Index 
    '''
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self, index):
        self._scheme = OrderedDict()
        self._scheme['dataset_type'] = None   
        if type(index) == types.StringTypes:
            self._scheme['index'] = tuple([index])
        else:
            self._scheme['index'] = tuple(index)
    
    def as_dict(self):
        ''' Returns a serial representation of the schema. Use the output of
        this method as the input of a serializer like json
        @return: OrderedDict''' 
        return copy(self._scheme)
    
    @abstractmethod
    def is_spatial(self):
        ''' A DataSet is spatial iff one of its components has spatial semantics.
        This method MUST be overwritten 
        @return: bool'''
        pass
    
    
    def is_abstract(self):
        '''A DataSet is abstract iff is not spatial
        @return: bool'''
        return not self.is_spatial()
    
    @property
    def dataset_type(self): 
        '''The dataset type. Currently the supported types are Table, Network 
        and Tree'''
        return self._scheme['dataset_type']
        
    @property
    def index(self):
        '''Is a list with the name of the Attributes that are used as index'''
        return self._scheme['index']
    
class TableScheme(DataSetScheme):
    '''The TableScheme describes the schema of a Table Dataset.
    Adds a field called attributes which is an ordered dict of AttributeSchemes'''
    def __init__(self, attributes, index):
        super(TableScheme, self).__init__(index)
        
        self._scheme['dataset_type'] = DataSetTypes.TABLE
        self._scheme['attributes'] = OrderedDict(attributes)
                
    @property
    def attributes(self):
        '''This is an OrededDict with the form - name:AttributeScheme'''
        return self._scheme['attributes']
    
    def is_spatial(self):
        ''' A DataSet is spatial iff one of its components has spatial semantics
        @return: bool'''
        return any( (a.is_spatial() for a in self.attributes) )

def negation(f):
    def wrapper(*args, **kwargs):
        return not f(*args, **kwargs)
    return wrapper
    
class AttributeScheme(object):
    '''The AttributeScheme describes the schema of any Attribute in any item '''
    def __init__(self, attribute_type, *args, **kwargs):
        '''@param attibute_type: One in AttributeTypes
        @param spatial: bool - The opposite of abstract
        @param key: bool - The opposite of value 
        @param shape: tuple - The shape ala numpy if multidimensional. () if Scalar
        @param continuous: bool - The opposite is discrete'''
        self._scheme = OrderedDict()

        self._scheme['attribute_type'] = getattr(AttributeTypes, attribute_type)
        
        self._scheme['spatial'] = kwargs.get('spatial', False)              # Vs Abstract
        self._scheme['key'] = kwargs.get('key', False)                      # Vs Value
        self._scheme['shape'] = kwargs.get('shape', ())                     # Shape of dimensions
        self._scheme['continuous'] = kwargs.get('continuous', False)        # Vs Discrete
        self._scheme['multivaluated'] = kwargs.get('multicaluated', False)  # TODO: Maybe this should be removed

    def as_dict(self):
        ''' Returns a serial representation of the schema. Use the output of
        this method as the input of a serializer like json
        @return: OrderedDict''' 
        return copy(self._scheme)
    
    def is_spatial(self):
        return self._scheme.get('spatial', False)

    def is_key(self):
        return self._scheme.get('key', False)

    def is_multidimensional(self):
        return len(self.shape) > 0
    
    def is_continuous(self):
        return self._scheme.get('continuous', False)
    
    @property
    def shape(self):
        return self._scheme.get('shape', ())

    is_abstract = negation(is_spatial)    
    is_value = negation(is_key)
    is_scalar = negation(is_multidimensional) 
    is_discrete = negation(is_continuous)