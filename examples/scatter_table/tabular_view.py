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
        self._col_names =  self._table.column_names()
        
        self.rcount = None
        self.ccount = None
    
    def rowCount(self, parent):
        self.rcount = self.rcount if self.rcount is not None else self._table.row_count()
        return self.rcount if not parent.isValid() else 0

    def columnCount(self, parent):
        self.ccount = self.ccount if self.ccount is not None else self._table.column_count()
        return self.ccount if not parent.isValid() else 0

    def data(self, index, role):
        if role != QtCore.Qt.DisplayRole: 
            return None  # No checkboxes
        row = self._data[ index.row() ]
        return row[ self._col_names[ index.column() ] ]
    

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
        self.dynfilter = None
        self.dynselect = None
        self._data_index = None

        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.MultiSelection)
        
    def set_table(self, table):
        self.table = table
        projection = {table.index : True}
        self._data_index = table.find({}, projection).get_data('c_list')[table.index]

    def set_dynfilter(self, dynfilter):
        self.dynfilter = dynfilter
        self.dynfilter.subscribe('change', self.on_filter_change)
        
    def set_dynselect(self, dynselect):
        self.dynselect = dynselect
        self.dynselect.subscribe('change', self.on_select_change)

    def on_filter_change(self, topic, msg):
        print 'topic: {0}, msg: {1}'.format(topic, msg)
        self.render_table()
    
    def on_select_change(self, topic, msg):
        print 'topic: {0}, msg: {1}'.format(topic, msg)
        self.render_table()
        
    def render_table(self):
        model = TDataTableModel()
        if self.dynfilter is not None:
            query = self.dynfilter.query(self.table.index)
            filtered_table = self.table.find(query)
            model.setTable(filtered_table)
        else:
            model.setTable(self.table)
        
        self.setModel(model)
        
        if self.dynselect is not None:
            reference = self.dynselect.ref
            selection_model = self.selectionModel()
            selection_model.clearSelection()
            for item in reference:
                self.selectRow(self._data_index.index(item))
                
        

