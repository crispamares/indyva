import pandas

class Table(object):
    def __init__(self, data_source, name='Unnamed Table'):
        self.data_source = data_source
        self.name = name
        self._df = pandas.DataFrame(data_source)

    def row(self, index):
        return Row(self, index)
    
    def rows(self, indices):
        return Rows([Row(self, i) for i in indices])

    def col(self, name):
        return self._df[name].tolist()

class RestrictedMethod(object):
    def __get__(self, obj, objtype):
        raise AttributeError("Access denied.")

def restrict_methods(*args):
    def wrap(cls):
        for attr in args:
            setattr(cls, attr, RestrictedMethod())
        return cls
    return wrap

class Rows(list):
    pass

class Row(object):
    def __init__(self, table, index):
        self.table = table
        self.__index = index
        self._serie = self.table._df.irow(self.index)

    def get_index(self):
        return self.__index
    def set_index(self, value):
        self.__index = value
        self._serie = self.table._df.irow(self.index)        
    def del_index(self):
        del self.__index
    
    index = property(get_index, set_index, del_index, "index's docstring")
        
    def keys(self):
        return self._serie.keys().tolist()
    
    def __getitem__(self, col):
        '''
        :param col: The column name
        '''
        return self._serie[col]

    def __len__(self):
        return len(self._serie)
    
    def __iter__(self):
        return self._serie.__iter__()
        
    def __repr__(self):
        return str(self._serie.to_dict())

    

