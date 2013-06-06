# -*- coding: utf-8 -*-
'''
Created on 20/03/2013

@author: jmorales
'''

import schemas

from abc import ABCMeta, abstractmethod
import exceptions

class ITable:
    '''
    This class is a DataSet Type, an abstraction of Tabluar Data
    '''
    __metaclass__ = ABCMeta
    
    def __init__(self, data, name='unnamed', schema=None):
        '''
        @param data: Tabular data. Supported forms are: dict, DataFrame
        @param name: The name of the table
        @param schema: column types and semantics. Supported forms are: dict or
            TableSchema
        '''
        self._name = name
        
        if schema is None:
            raise exceptions.NotImplementedError("Schema infer is not yet implemented") 
        
        if isinstance(schema, dict):
            self._schema = schemas.TableSchema(schema['attributes'], schema['index'])
        elif isinstance(schema, schemas.TableSchema):
            self._schema = schema 
            
        self._prepare_data(data)
        
    @abstractmethod
    def _prepare_data(self, data):
        pass

    @property
    def name(self):
        return self._name
    
    @abstractmethod
    def to_dict(self):
        pass
    
    @abstractmethod
    def to_DataFrame(self):
        pass
    
    @abstractmethod
    def find(self, spec=None, attributes=None, skip=0, limit=0, sort=None):
        '''
        @return: TableView
        
        @param spec: a dict object specifying elements which
        must be present for a row to be included in the
        result set
        @param attributes: a list of attributes names that should be
        returned in the result set (keys will always be
        included), or a dict specifying the attributes to return
        @param skip: the number of rows to omit (from
        the start of the result set) when returning the results
        @param limit: the maximum number of results to
        return
        @param sort: Takes a list of (attribute, direction) pairs. 
        '''
        pass
