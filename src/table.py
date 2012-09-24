import pandas

class Table(object):
    def __init__(self, data_source, name='Unnamed Table'):
        self.data_source = data_source
        self.name = name
        self.df = pandas.DataFrame(data_source)
    
    def rows(self, indices):
        return Rows([Row(self, i) for i in indices])

class Rows(list):
    pass

class Row(object):
    def __init__(self, table, index):
        self.table = table
        self.index = index
        
    def __str__(self):
        return str(self.table.rows([self.index]).as_matrix().tolist())



