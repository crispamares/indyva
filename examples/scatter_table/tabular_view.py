'''
Created on Jun 27, 2013

@author: crispamares
'''

from PyQt4 import QtGui, QtCore

from indyva.dataset.table import TableView
from indyva.epubsub import hub

class TDataTableModel(QtCore.QAbstractTableModel):
        
    def setTable(self, table):
        self._table = table
        self._data = self._table.get_data('c_list')
        self._col_names =  self._table.column_names()
        
        # The following fails because multiple view_args is not already implemented 
        #self.data_index = table.find({}, {table.index : True}).get_data('c_list')[table.index]
        
        self.data_index = self._data[table.index]
        
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
        col = self._data[self._col_names[ index.column() ] ]
        #row = self._data[ index.row() ]
        return col[ index.row() ]# [ self._col_names[ index.column() ] ]
    

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
        self.highlight = None
        
        self.dirty = True

        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.MultiSelection)

        hub.instance().subscribe('r:', self.on_render)
        
    def set_table(self, table):
        self.table = table
        self.dirty = True

    def set_dynfilter(self, dynfilter):
        self.dynfilter = dynfilter
        self.dynfilter.subscribe('change', self.on_filter_change)
        self.dirty = True
        
    def set_highlight(self, dynselect):
        self.highlight = dynselect
        self.highlight.subscribe('change', self.on_hightlight_change)
        self.dirty = True

    def on_filter_change(self, topic, msg):
        print 'topic: {0}, msg: {1}'.format(topic, msg)
        #self.render_table()
        self.dirty = True
    
    def on_hightlight_change(self, topic, msg):
        print 'topic: {0}, msg: {1}'.format(topic, msg)
        #self.render_table()
        self.dirty = True
        
    def on_render(self, topic, msg):
        if not self.dirty:
            return        
        self.render_table()
        
    def render_table(self):
        self.dirty = False
        model = TDataTableModel()
        if self.dynfilter is not None:
            query = self.dynfilter.query
            projection = self.dynfilter.projection
            filtered_table = self.table.find(query, projection)
            model.setTable(filtered_table)
        else:
            model.setTable(self.table)
        
        self.setModel(model)
        
        if self.highlight is not None:
            reference = self.highlight.reference
            selection_model = self.selectionModel()
            selection_model.clearSelection()
            existing_ref = set(reference).intersection(model.data_index)
            for item in existing_ref:
                self.selectRow(model.data_index.index(item))
                

