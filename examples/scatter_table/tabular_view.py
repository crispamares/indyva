'''
Created on Jun 27, 2013

@author: crispamares
'''

from PyQt4 import QtGui, QtCore

from dataset.table import TableView

class TDataTableModel(QtCore.QAbstractTableModel):
    def setTable(self, table):
        self._table = table
        self._data = self._table.get_data()
        
        self.rcount = None
        self.ccount = None
    
    def rowCount(self, parent):
        self.rcount = self.rcount if self.rcount is not None else self._table.row_count()
        return self.rcount if not parent.isValid() else 0

    def columnCount(self, parent):
        self.ccount = self.ccount if self.ccount is not None else self._table.column_count() - 1
        return self.ccount if not parent.isValid() else 0

    def data(self, index, role):
        row = self._data[ index.row() ]
        return row[ self._table._schema.attributes.keys()[ index.column() ] ]

class TabularView(QtGui.QTableView):
    '''
    A table widget
    '''

    def __init__(self, parent):
        '''
        Constructor
        '''
        QtGui.QTableView.__init__(self, parent)
        self.table = None
        
    def set_table(self, table):
        self.table = table
        
    def render_table(self):
        model = TDataTableModel()
        model.setTable(self.table)
        self.setModel(model)

