import pandas as pn

class Selection(object):
    def __init__(self, table, index=None):
        self._table = table
        self._index = pn.Index(index) if index is not None else table.index
        self.name = 'Unnamed Selection'

    @property
    def table(self):
        return self._table
    @property
    def index(self):
        return self._index

    def replace(self, index):
        self._index = pn.Index(index)

    def union(self, index):
        self._index = self.index.union(pn.Index(index))

    def substract(self, index):
        self._index = self.index - index
        
    def toggle(self):
        self._index = self.table.index - self.index 

    def intersect(self, index):
        self._index = self.index.intersection(index)
    
    def selected(self):
        return self.table.ix[self.index]
    
    def __eq__(self, other):
        return self.table is other.table and pn.np.all(self.index == other.index)
    
    def __repr__(self):
        return self.name+' ('+str(self.index)+')'
    
    
class MarkSelection(Selection):
    def __init__(self, color, table, index=None):
        Selection.__init__(self, table, index)
        self.color = color
    
    
        


