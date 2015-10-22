'''
Created on 26/03/2013

@author: crispamares
'''
from indyva.epubsub.abc_publisher import IPublisher, pub_result
from indyva.epubsub.bus import Bus
from indyva.core.names import INamed
from indyva.core.grava import IDefined, register

from .abc_table import ITable, ITableView
from .mongo_backend.table import MongoTable
from . import schemas


class TableView(ITableView, IPublisher, INamed):
    _backend = MongoTable

    def __init__(self, parent, view_args, prefix=''):
        '''
        :param str prefix: Prepended to the name creates the oid
        '''
        if parent is not None:
            self._backend = parent._backend
            self._schema = parent._schema
            bus = parent._bus
            INamed.__init__(self, self._new_name(parent.name), prefix=prefix)
        else:
            bus = Bus(prefix= '{0}{1}:'.format(prefix, self.name))

        topics = ['add', 'update', 'remove']
        IPublisher.__init__(self, bus, topics)
        ITableView.__init__(self, parent, view_args)

    def get_data(self, outtype='rows'):
        return self._backend.get_view_data(view_args=self.view_args, outtype=outtype)

    def find(self, query=None, projection=None, skip=0, limit=0, sort=None):
        view_args = dict(query=query, projection=projection, skip=skip, limit=limit, sort=sort)
        return TableView(parent=self, view_args=view_args)

    def find_one(self, query=None, projection=None, skip=0, sort=None):
        view_args = dict(query=query, projection=projection, skip=skip, limit=1, sort=sort)
        return self._backend.find_one( view_args=self._merge_args(self.view_args, view_args) )

    def distinct(self, column, as_view=False):
        if not as_view:
            return self._backend.distinct(column, view_args=self.view_args)
        else:
            return self.aggregate([{'$group' : {'_id': '$'+column}},
                                   {'$project' : {column: '$_id'}}])

    def aggregate(self, pipeline):
        view_args = {'pipeline' : pipeline}
        return TableView(parent=self, view_args=view_args)

    def index_items(self):
        return self._backend.index_items(view_args=self.view_args)

    def row_count(self):
        return self._backend.row_count(view_args=self.view_args)

    def column_count(self):
        return self._backend.column_count(view_args=self.view_args)

    def column_names(self):
        return self._backend.column_names(view_args=self.view_args)


@register("table")
class Table(ITable, TableView, INamed, IDefined):
    _backend = MongoTable

    def __init__(self, name=None, schema=None, prefix=''):
        '''
        :param str name: If a name is not provided, an uuid is generated
        :param schema: The schema associated to the data.
        :param str prefix: Prepended to the name creates the oid
        '''
        self._backend = self._backend(name, schema, prefix=prefix)
        INamed.__init__(self, name, prefix=prefix)
        ITable.__init__(self, schema)
        TableView.__init__(self, None, None, prefix)

    def _check_index(self, row_or_rows):
        '''Raise a ValueError if any row does not have valid index keys'''
        rows = row_or_rows if isinstance(row_or_rows, list) else [row_or_rows]
        indices = self.index if isinstance(self.index, tuple) else tuple([self.index])
        for row in rows:
            if not all([row.has_key(i) for i in indices]):
                raise ValueError('Every row needs valid index: {0}'.format(indices))

    def data(self, data):
        ''' SetUp the data
        @param data: Tabular data. Supported forms are: dict, DataFrame
        @return: self
        '''
        if self._schema is None:
            self._schema = schemas.TableSchema.infer_from_data(data)
        self._backend.data(data)
        self._backend._schema = self._schema  ######TODOOOOOOOOOOO-----------------------------
        return self

    @pub_result('add')
    def insert(self, row_or_rows):
        self._check_index(row_or_rows)
        msg = self._backend.insert(row_or_rows)
        return msg

    @pub_result('update')
    def update(self, query=None, update=None, multi=True, upsert=False):
        #TODO: Improve the message
        msg = self._backend.update(query, update, multi, upsert)
        return msg

    @pub_result('remove')
    def remove(self, query):
        msg = self._backend.remove(query)
        return msg

    @property
    def grammar(self):
        gv = {"type":"table",
              "name":self.name,
              "schema":self.schema.for_json()}
        return gv

    @classmethod
    def build(cls, grammar, objects=None):
        self = cls(name=grammar['name'],
                   schema=grammar['schema'])
        return self

    def add_column(self, name, attribute_schema):
        ''' Add a new column schema to the table
        @param name: str The name of the new column. Two columns with the same
        name are not allowed
        @param attribute_schema: AttributeSchema
        '''
        self._schema.add_attribute(name, attribute_schema)


    @pub_result('update')
    def rename_columns(self, changes):
        ''''Renames a column in the table and in the schema
        @param changes: dict The changes in the format {old_name: new_name}
        '''
        msg = self._backend.rename_columns(changes)
        for old_name, new_name in changes.items():
            self._schema.rename_attribute(old_name, new_name)
        return msg


    def add_derived_column(self, name, attribute_schema, inputs, function):
        '''
        @param name: str The name of the new column. Two columns with the same
        name are not allowed
        @param attribute_schema: AttributeSchema
        @param inputs: list with the names of the attributes that will be the
        inputs for the function that computes the derived value. Allways that
        those inputs change the derived column values are recomputed
        @function: dict or RemoteFunction This code will be executed once per row
        Returns the derived value. The dict statement use the core grammar and has
        access to the inputs with $name_of_input. The RemoteFunction will be
        invoked with a dict of inputs {name_of_input:value}
        '''
        pass
