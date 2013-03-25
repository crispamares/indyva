# -*- coding: utf-8 -*-
'''
Created on 20/03/2013

@author: jmorales
'''

import schemas
from mongo_backend.table import MongoTable

from abc import ABCMeta, abstractmethod
import exceptions

class ITable:
    '''
    This class is a DataSet Type, an abstraction of Tabluar Data
    '''
    __metaclass__ = ABCMeta
    
    def __init__(self, data, schema=None):
        '''
        @param data: Tabular data. Supported forms are: dict, DataFrame
        @param schema: column types and semantics. Supported forms are: dict or
            TableSchema
        '''
        if schema is None:
            raise exceptions.NotImplementedError("Schema infer is not yet implemented") 
        
        if isinstance(schema, dict):
            self._schema = schemas.TableSchema(dict['attributes'], dict['index'])
        elif isinstance(schema, schemas.TableSchema):
            self._schema = schema 
            
        self._adquire_data(data)
        
    @abstractmethod
    def _adquire_data(self, data):
        pass
        
class Table(ITable):
    _backend = MongoTable
    
    @abstractmethod
    def _adquire_data(self, data):
        self._backend._adquire_data(data)