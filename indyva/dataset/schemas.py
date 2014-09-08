# -*- coding: utf-8 -*-
'''
Any dataset in indyva must be coupled with a description. This
description is what we call a Schema.

There are two level of descriptions in a dataset. The first one is
composed by the features of the dataset itself and, more interesting,
the second one is composed by the features of every attribute in the
dataset.

:author: Juan Morales
:author: Jose Miguel Espadero
'''
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import types
from copy import copy

import pandas as pd
import json
from indyva import for_json_bridge

DataSetTypes = type("DataSetTypes", (),
                    dict(TABLE='TABLE', NETWORK='NETWORK', TREE='TREE'))
AttributeTypes = type("AttributeTypes", (),
                      dict(CATEGORICAL='CATEGORICAL',
                           ORDINAL='ORDINAL',
                           QUANTITATIVE='QUANTITATIVE',
                           UNKNOWN='UNKNOWN'))


class DataSetSchema(object):
    '''
    A DataSet Schema is the definition of the related DataSet. At least, inside the
    schema are defined the DataSetType and Index.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, index):
        self._schema = OrderedDict()
        self._schema['dataset_type'] = None

        if index is None:
            raise ValueError("Every DataSetSchema needs an index, None provided")
        elif isinstance(index, types.StringTypes):
            self._schema['index'] = index
        else:
            self._schema['index'] = tuple(index)

    def for_json(self):
        '''
        Returns a serial representation of the schema. Use the output of
        this method as the input of a serializer like json

        :returns: OrderedDict
        '''
        return copy(self._schema)

    @abstractmethod
    def is_spatial(self):
        '''
        A DataSet is spatial iff one of its components has spatial semantics.
        This method MUST be overwritten

        :returns: bool
        '''
        pass

    def is_abstract(self):
        '''
        A DataSet is abstract iff is not spatial

        :returns: bool
        '''
        return not self.is_spatial()

    @property
    def dataset_type(self):
        '''
        The dataset type. Currently the supported types are Table, Network
        and Tree
        '''
        return self._schema['dataset_type']

    @property
    def index(self):
        '''
        Is a string or a tuple with the name of the Attributes that are
        used as index
        '''
        return self._schema['index']

    def __repr__(self):
        return json.dumps(dict(attributes=dict(self._schema['attributes']),
                               index=self._schema['index']),
                          default=for_json_bridge,
                          indent=True)


class TableSchema(DataSetSchema):
    '''
    The TableSchema describes the schema of a Table Dataset.

    Adds a field called attributes which is an ordered dict of
    AttributeSchemas
    '''
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
        '''
        A DataSet is spatial iff one of its components has spatial semantics

        :returns: bool
        '''
        return any( (a.is_spatial() for a in self.attributes) )

    def add_attribute(self, name, attribute_schema):
        '''
        Add a new attribute to the schema of the table

        :param name: str must be unique in the schema of the table
        :param attribute_schema: AttributeSchema, AttributeType or
        kwargs of AttributeSchema's __init__ .
        '''
        if name in self._schema['attributes']:
            raise ValueError('Name must be unique in the schema')
        if isinstance(attribute_schema, types.StringTypes):
            attribute_schema = AttributeSchema(attribute_schema)
        if isinstance(attribute_schema, dict):
            attribute_schema = AttributeSchema(**attribute_schema)
        self._schema['attributes'][name] = attribute_schema

    @staticmethod
    def infer_from_data(data):
        '''
        This static method acts as a factory method of TableSchema

        Accepts lists of rows (dicts) or a pandas.DataFrame

        Delegates the inference of each attribute_schema to the
        AttributeSchema.infer_from_data method.

        The index of the schema will be the first attribute identified
        as a key

        :param data: lists of rows (dicts) or a pandas.DataFrame
        :returns: TableSchema
        '''
        if isinstance(data, pd.DataFrame):
            df = data
        elif isinstance(data, list):
            df = pd.DataFrame(data)
            # Key needs to be infered

        schemas = OrderedDict()
        index = None
        for column in df.columns:
            schemas[column] = AttributeSchema.infer_from_data(df[column])
            if index is None:
                index = column if schemas[column].is_key() else None

        return TableSchema(schemas, index)



def negation(f):
    def wrapper(*args, **kwargs):
        return not f(*args, **kwargs)
    return wrapper


class AttributeSchema(object):
    '''The AttributeSchema describes the schema of any Attribute in any item '''
    def __init__(self, attribute_type, *args, **kwargs):
        '''
        :param attribute_type: One in AttributeTypes
        :param spatial: bool - The opposite of abstract
        :param key: bool - The opposite of value
        :param shape: tuple - The shape ala numpy if multidimensional. () if Scalar
        :param continuous: bool - The opposite is discrete

        :param infered: bool - True if the schema is infered from data
        '''
        self._schema = OrderedDict()

        self._schema['attribute_type'] = getattr(AttributeTypes, attribute_type)

        self._schema['spatial'] = kwargs.get('spatial', False)              # Vs Abstract
        self._schema['key'] = kwargs.get('key', False)                      # Vs Value
        self._schema['shape'] = kwargs.get('shape', ())                     # Shape of dimensions
        self._schema['continuous'] = kwargs.get('continuous', False)        # Vs Discrete

        self._infered = kwargs.get('infered', False)

    def for_json(self):
        '''
        Returns a serial representation of the schema. Use the output of
        this method as the input of a serializer like json

        :returns: OrderedDict
        '''
        return copy(self._schema)

    @property
    def attribute_type(self):
        return self._schema['attribute_type']

    @attribute_type.setter
    def attribute_type(self, value):
        self._schema['attribute_type'] = getattr(AttributeTypes, value)

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

    @shape.setter
    def shape(self, value):
        self._schema['shape'] = value

    is_abstract = negation(is_spatial)
    is_value = negation(is_key)
    is_scalar = negation(is_multidimensional)
    is_discrete = negation(is_continuous)

    def set_spatial(self, value):
        self._schema['spatial'] = value

    def set_key(self, value):
        self._schema['key'] = value

    def set_continuous(self, value):
        self._schema['continuous'] = value

    @property
    def infered(self):
        return self._infered

    @infered.setter
    def infered(self, value):
        self._infered = value

    def __repr__(self):
        return 'AttributeSchema({0})'.format(self._schema)


    @staticmethod
    def infer_from_data(data):
        '''
        This static method acts as a factory method of AttributeSchema

        Accepts a list containing the values of the attribute or a
        pandas.Series

        :param list data: list containing the values of the attribute
        or a pandas.Series
        :returns: AttributeSchema
        '''

        if isinstance(data, pd.Series):
            s = data
        elif isinstance(data, list):
            s = pd.Series(data)

        attribute_schema = None

        if s.dtype == float:
            attribute_schema = AttributeSchema._infer_from_float(s)
        elif s.dtype == int:
            attribute_schema = AttributeSchema._infer_from_int(s)
        elif s.dtype == object:
            if s.valid().apply(lambda x: isinstance(x, types.StringTypes)).all():
                attribute_schema = AttributeSchema._infer_from_str(s)
            elif (s.valid().apply(type) == list).all():
                attribute_schema = AttributeSchema._infer_from_list(s)

        return attribute_schema if attribute_schema else AttributeSchema('UNKNOWN')


    @staticmethod
    def _infer_from_float(series):
        attribute_schema = AttributeSchema(AttributeTypes.QUANTITATIVE,
                                           key = False,
                                           spatial = False,
                                           shape = tuple(),
                                           continuous = True,
                                           infered = True)
        return attribute_schema

    @staticmethod
    def _infer_from_int(series):
        schema = dict(attribute_type = AttributeTypes.QUANTITATIVE,
                      key = False,
                      spatial = False,
                      shape = tuple(),
                      continuous = False,
                      infered = True)

        if series.nunique() <= series.size * 0.25:
            schema.update(attribute_type=AttributeTypes.CATEGORICAL)
        elif (series.nunique() == series.size and
              series.max() - series.min() == series.size - 1):
            schema.update(attribute_type= AttributeTypes.ORDINAL,
                          key= True)

        return AttributeSchema(**schema)

    @staticmethod
    def _infer_from_str(series):
        schema = dict(attribute_type = AttributeTypes.CATEGORICAL,
                      key = False,
                      spatial = False,
                      shape = tuple(),
                      continuous = False,
                      infered = True)

        if series.nunique() == series.size:
            schema.update(key=True)

        return AttributeSchema(**schema)

    @staticmethod
    def _infer_from_list(series):
        shape = series.valid().apply(pd.np.shape).unique()[0]

        attribute_schema = AttributeSchema(AttributeTypes.QUANTITATIVE,
                                           key = False,
                                           spatial = True,
                                           shape = shape,
                                           continuous = True,
                                           infered = True)
        return attribute_schema
