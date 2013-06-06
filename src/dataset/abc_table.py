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
        
    def find(self, args):
        pass # TODO: Not implemented
