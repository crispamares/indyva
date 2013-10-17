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
                           ORDINAL='ORDINAL',
                           QUANTITATIVE='QUANTITATIVE',
                           UNKNOWN='UNKNOWN'))


class DataSetSchema:
    '''
    A DataSet Schema is the definition of the related DataSet. Inside the 
    schema at least are defined the DataSetType, and Index 
    '''
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self, index):
        self._schema = OrderedDict()
        self._schema['dataset_type'] = None 
        if isinstance(index, types.StringTypes):
            self._schema['index'] = index
        else:
            self._schema['index'] = tuple(index)
    
    def to_dict(self):
        ''' Returns a serial representation of the schema. Use the output of
        this method as the input of a serializer like json
        @return: OrderedDict''' 
        return copy(self._schema)
    
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
        return self._schema['dataset_type']
        
    @property
    def index(self):
        '''Is a string or a tuple with the name of the Attributes that are used 
        as index'''
        return self._schema['index']
    
class TableSchema(DataSetSchema):
    '''The TableSchema describes the schema of a Table Dataset.
    Adds a field called attributes which is an ordered dict of AttributeSchemas'''
    def __init__(self, attributes, index):
        super(TableSchema, self).__init__(index)
        
        self._schema['dataset_type'] = DataSetTypes.TABLE
        self._schema['attributes'] = OrderedDict()
        for name in attributes:
            self.add_attribute(name, attributes[name])

    @property
    def attributes(self):
        '''This is an OrededDict with the form - name:AttributeSchema'''
        return self._schema['attributes']
    
    def is_spatial(self):
        ''' A DataSet is spatial iff one of its components has spatial semantics
        @return: bool'''
        return any( (a.is_spatial() for a in self.attributes) )
    
    def add_attribute(self, name, attribute_schema):
        ''' Add a new attribute to the schema of the table
        @param name: str must be unique in the schema of the table
        @param attribute_schema: AttributeSchema, AttributeType or kwargs 
            of AttributeSchema's __init__ .            
        '''
        if self._schema['attributes'].has_key(name):
            raise ValueError('Name must be unique in the schema')
        if isinstance(attribute_schema, types.StringTypes):
            attribute_schema = AttributeSchema(attribute_schema)
        if isinstance(attribute_schema, dict):
            attribute_schema = AttributeSchema(**attribute_schema)
        self._schema['attributes'][name] = attribute_schema
         
        
def negation(f):
    def wrapper(*args, **kwargs):
        return not f(*args, **kwargs)
    return wrapper
    
class AttributeSchema(object):
    '''The AttributeSchema describes the schema of any Attribute in any item '''
    def __init__(self, attribute_type, *args, **kwargs):
        '''@param atribute_type: One in AttributeTypes
        @param spatial: bool - The opposite of abstract
        @param key: bool - The opposite of value 
        @param shape: tuple - The shape ala numpy if multidimensional. () if Scalar
        @param continuous: bool - The opposite is discrete'''
        self._schema = OrderedDict()

        self._schema['attribute_type'] = getattr(AttributeTypes, attribute_type)
        
        self._schema['spatial'] = kwargs.get('spatial', False)              # Vs Abstract
        self._schema['key'] = kwargs.get('key', False)                      # Vs Value
        self._schema['shape'] = kwargs.get('shape', ())                     # Shape of dimensions
        self._schema['continuous'] = kwargs.get('continuous', False)        # Vs Discrete
        self._schema['multivaluated'] = kwargs.get('multivaluated', False)  # TODO: Maybe this should be removed

    def to_dict(self):
        ''' Returns a serial representation of the schema. Use the output of
        this method as the input of a serializer like json
        @return: OrderedDict''' 
        return copy(self._schema)
    
    @property
    def attribute_type(self):
        return self._schema['attribute_type']
    
    def is_spatial(self):
        return self._schema.get('spatial', False)

    def is_key(self):
        return self._schema.get('key', False)

    def is_multidimensional(self):
        return len(self.shape) > 0
    
    def is_continuous(self):
        return self._schema.get('continuous', False)
    
    @property
    def shape(self):
        return self._schema.get('shape', ())

    is_abstract = negation(is_spatial)    
    is_value = negation(is_key)
    is_scalar = negation(is_multidimensional) 
    is_discrete = negation(is_continuous)
    
    def __repr__(self):
        return 'AttributeSchema({0})'.format(self._schema)
