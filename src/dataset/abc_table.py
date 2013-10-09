# -*- coding: utf-8 -*-
'''
Created on 20/03/2013

@author: jmorales
'''

import schemas

from abc import ABCMeta, abstractmethod
import exceptions
from copy import copy

class ITableView(object):
    
    __metaclass__ = ABCMeta

    _id_counter = 0

    def __init__(self, parent, view_args):        
        self._view_args =  [{}] if view_args is None else self._merge_args(parent.view_args, view_args)   
        
    def _merge_args(self, parent_args, new_args):
        if len(parent_args) == 1:
            view_args = copy(parent_args) if len(parent_args[0]) != 0 else []
            view_args.append(new_args)
        else:
            view_args = copy(parent_args)
            if len(new_args) == 0:
                view_args.append(new_args)
        return view_args
        
    def _new_name(self, prefix=''):
        cls = self.__class__
        cls._id_counter += 1
        return prefix+'.v{0}'.format(cls._id_counter)
        
    @property
    def name(self):
        return self._name
    
    @property
    def index(self):
        return self._schema.index

    @property
    def schema(self):
        return self._schema
    
    @property
    def view_args(self):
        return self._view_args
    
    @abstractmethod
    def find(self, query=None, projection=None, skip=0, limit=0, sort=None):
        '''
        @return: TableView
        
        @param query: a dict object specifying elements which
        must be present for a row to be included in the
        result set
        @param projection: a list of projection names that should be
        returned in the result set (keys will always be
        included), or a dict specifying the projection to return
        @param skip: the number of rows to omit (from
        the start of the result set) when returning the results
        @param limit: the maximum number of results to
        return
        @param sort: Takes a list of (attribute, direction) pairs. 
        '''
        pass
    
    @abstractmethod
    def get_data(self, outtype='rows'):
        pass 
    
    @abstractmethod
    def find_one(self):
        pass
    
    @abstractmethod
    def distinct(self, column):
        pass
    
    @abstractmethod
    def aggregate(self, pipeline):
        pass
       
    @abstractmethod
    def index_items(self):
        pass
    
    @abstractmethod
    def row_count(self):
        pass
    
    @abstractmethod
    def column_count(self):
        pass
    
    @abstractmethod    
    def column_names(self):
        pass



class ITable(ITableView):
    '''
    This class is a DataSet Type, an abstraction of Tabluar Data
    '''
    __metaclass__ = ABCMeta
    
    def __init__(self, name='unnamed', schema=None):
        '''
        @param name: The name of the table
        @param schema: column types and semantics. Supported forms are: dict or
            TableSchema
        '''
        self._name = name
        
        if schema is None:
            raise exceptions.NotImplementedError("Inferring the schema is not yet implemented") 
        
        if isinstance(schema, dict):
            self._schema = schemas.TableSchema(schema['attributes'], schema['index'])
        elif isinstance(schema, schemas.TableSchema):
            self._schema = schema 

        ITableView.__init__(self, parent=None, view_args=None)
    
    @abstractmethod
    def data(self, data):
        ''' SetUp the data  
        @param data: Tabular data. Supported forms are: dict, DataFrame
        @return: self
        '''
        pass   
        
