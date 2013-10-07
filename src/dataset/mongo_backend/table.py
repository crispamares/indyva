from __future__ import absolute_import
from ..abc_table import ITable
from .connection import Connection

from functools import wraps
import pandas as pn
import exceptions
from types import DictType
from pymongo.cursor import Cursor 

''' The mongo backend stores each analysis as a different database. And 
each dataset as a different collection.

The database used as analysis namespace is setted in the connection module
'''

def if_pipeline(pipeline_f):
    '''
    This decorator calls pipeline_f instead of the wrapped function if
    view_args needs to be resolved using the aggregation framework
    Needs that the 'view_args' arg is in kwargs 
    '''
    def wrap(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if self._is_pipeline(kwargs['view_args']):
                return pipeline_f(self, *args, **kwargs)
            return f(self, *args, **kwargs)
        return wrapper
    return wrap

class MongoTable(ITable):
    
    def __init__(self, *args, **kargs):
        ''' The MongoTable is an operational database. This means that even when there is a 
        collection in the DB with the same name, the user has to be provided data to use.
        Note: This convention might be changed only for performance reasons.
        '''
        self.connection = Connection()
        ITable.__init__(self, *args, **kargs)

        db = self.connection.db
        db.drop_collection(self.name)
        self._col = db[self.name]

    def _serialize_data(self, data, outtype):
        '''
        @param data: list or pymongo.cursor.Cursor
        @param outtype: one of ['rows', 'c_list']
        '''
        if isinstance(data, Cursor):
            data = list(data)
        
        if outtype == 'rows':
            return data
        if outtype == 'c_list':
            df = pn.DataFrame(data)
            return df.to_dict('list')
        raise exceptions.NotImplementedError()

    def _is_pipeline(self, view_args):
        is_pipeline = ( not isinstance(view_args, dict)
                      and ( len(view_args) == 1 and 'pipeline' in view_args[0]
                            or len(view_args) > 1)
                     )
        return is_pipeline

    def _to_pipeline(self, view_args):
        pipeline = []
        for v in view_args:
            if v.get('pipeline', None):
                pipeline += v['pipeline']
                continue
            if v.get('query', None):
                pipeline.append({'$match': v['query']})
            if v.get('skip', None):
                pipeline.append({'$skip': v['skip']})
            if v.get('limit', None):
                pipeline.append({'$limit': v['limit']})
            if v.get('sort', None):
                pipeline.append({'$sort': v['sort']})
            if v.get('projection', None):
                projection = v['projection']
                projection.update({'_id':False})
                pipeline.append({'$project': projection})
        return pipeline    

    def get_data(self , outtype='rows'):
        return self._serialize_data(self.find(), outtype)

    def get_view_data(self, view_args=[{}], outtype='rows'):
        if isinstance(view_args, dict):
            view_args = [view_args]
        if len(view_args) == 1:
            if 'pipeline' in view_args[0]:
                data = self.aggregate(view_args[0]['pipeline'])
            else:
                data = self.find(**view_args[0])    
        elif len(view_args) > 1: 
            print 'TO PIP', view_args
            pipeline = self._to_pipeline(view_args)
            data = self.aggregate(pipeline)    
        
        return self._serialize_data(data, outtype)
        
    def aggregate(self, pipeline):
        print 'PIPELINE:', pipeline
        return self._col.aggregate(pipeline)['result']

    def data(self, data):
        rows = []
        if isinstance(data, pn.DataFrame):
            for i in range(len(data)):
                rows.append(data.ix[i].to_dict())
        elif isinstance(data, list):
            rows = data
        
        self._col.insert(rows)
        return self

    def find(self, query=None, projection=None, skip=0, limit=0, sort=None):
        projection = projection if isinstance(projection, DictType) else {} 
        projection.update({'_id':False})
        return self._col.find(query, fields=projection, skip=skip, limit=limit, sort=sort)
        
    def find_one(self, query=None, projection=None, skip=0, limit=0, sort=None):
        projection = projection if isinstance(projection, DictType) else {} 
        projection.update({'_id':False})
        return self._col.find_one(query, fields=projection, skip=skip, limit=limit, sort=sort)
    
    def distinct(self, column, view_args):
        return self.find(**view_args[0]).distinct(column)
    
    def index_items(self, view_args):
        return self.find(**view_args[0]).distinct(self.index)

    def _row_count_pipeline(self, view_args):
        return len(self.aggregate(self._to_pipeline(view_args)))
    
    @if_pipeline(_row_count_pipeline)
    def row_count(self, view_args):
        return self.find(**view_args[0]).count()
    
    def column_count(self, view_args):
        return len(self.column_names(view_args=view_args))

    def _column_names_pipeline(self, view_args):
        keys_set = set()
        for row in self.aggregate(self._to_pipeline(view_args)):
            keys_set.update(row.keys())
        return list(keys_set.intersection(self._schema.attributes.keys()))

    @if_pipeline(_column_names_pipeline)
    def column_names(self, view_args):
        keys_set = set()
        for row in self.find(**view_args[0]):
            keys_set.update(row.keys())
        return list(keys_set.intersection(self._schema.attributes.keys()))

    #===========================================================================
    #    Only Table (Not ViewTable) methods 
    #===========================================================================

    def insert(self, row_or_rows):
        reference = []
        rows = row_or_rows if isinstance(row_or_rows, list) else [row_or_rows]
        attributes = set()
        
        for row in rows:
            attributes.update(row.keys())
            reference.append(row[self.index])
            
        self._col.insert(row_or_rows)
        return {'items':reference, 'attributes': list(attributes)}

    def update(self, query=None, update=None, multi=True, upsert=False):
        reference = []
        if multi:
            for row in self.find(query, {self.index: True}):
                reference.append(row[self.index])
        else:
            row = self.find_one(query, {self.index: True})
            reference.append(row[self.index])
        attributes = update.get('$set', update).keys()
          
        self._col.update(query, update, multi, upsert)
        return {'items':reference, 'attributes': attributes}

    def remove(self, query):
        reference = []
        attributes = set()
        for row in self.find(query):
            attributes.update(row.keys())
            reference.append(row[self.index])
        # TODO Check compatibility 2.2 and 2.4 with safe argument
        self._col.remove(query, safe=True)
        return {'items':reference, 'attributes': list(attributes)}
    
