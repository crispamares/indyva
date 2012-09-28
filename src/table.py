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

class RestrictingMetaWrapper(type):
    def __new__(cls, name, bases, dic):
        block = dic.get('_block', [])

        for attr in block:
            dic[attr] = RestrictedMethod()

        return type.__new__(cls, name, bases, dic) # note we inject the base class here



def restrict_methods(*args):
    def wrap(cls):
        for attr in args:
            setattr(cls, attr, RestrictedMethod())
        return cls
    return wrap


#class RestrictingMetaWrapper(type):
#    def __new__(cls, name, bases, dic):
#        wrapped = dic['_w']
#        block = dic.get('_block', [])
#
#        new_class_dict = {}
#        new_class_dict.update(wrapped.__dict__)
#        for attr_to_block in block:
#            del new_class_dict[attr_to_block]
#        new_class_dict.update(dic)
#        
#        return type.__new__(cls, name, bases, new_class_dict)
#
class RestrictingWrapper(object):
    def __init__(self, w, block):
        self._w = w
        self._block = block
    def __getattr__(self, n):
        if n in self._block:
            raise AttributeError, n
        return getattr(self._w, n)


class Row2(RestrictingWrapper):
    def __init__(self, *args, **kargs):
        w = pandas.Series(*args, **kargs)
        block = ['index']
        RestrictingWrapper.__init__(self, w, block)

class Row3(pandas.Series):
    __metaclass__ = RestrictingMetaWrapper
    _block = ['max']
    
        

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

    

