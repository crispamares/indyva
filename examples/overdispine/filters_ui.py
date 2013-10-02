# -*- coding: utf-8 -*-
'''
Created on 20/09/2013

@author: jmorales
'''
from PyQt4 import QtGui, QtCore
from dynamics.dfilter import DynFilter

class CategoricalFilterView(QtGui.QGroupBox):
    '''
    This class provide a filter menu for categorical column 
    '''

    def __init__(self, *args, **kwargs):
        QtGui.QGroupBox.__init__(self, *args, **kwargs)
        self.v_layout = QtGui.QVBoxLayout(self)
        self.view = QtGui.QListView(self)   
        self.v_layout.addWidget(self.view)
        self.setLayout(self.v_layout)       
        
    def get_in_dock(self, parent):
        dock = QtGui.QDockWidget(self.title(), parent)
        dock.setWidget(self.view)
        return dock
        
class CategoricalFilterModel(QtCore.QAbstractListModel):
    
    def __init__(self, table, column, *args, **kwargs):
        QtCore.QAbstractListModel.__init__(self, *args, **kwargs)
        self.rcount = None
        self._table = table # TODO: Test that the column is a categorical attribute 
        self.selection = None
        self._column = column

        self._data = sorted(self._table.distinct(self._column))
    
    def rowCount(self, parent):
        self.rcount = len(self._data)
        return self.rcount if not parent.isValid() else 0
    
    def data(self, index, role):
        if role != QtCore.Qt.DisplayRole: 
            return None  # No checkboxes
        if role == QtCore.Qt.CheckStateRole:
            return QtCore.Qt.Checked
        return self._data[index.row()]
    
class CategoricalFilterItemModel(QtGui.QStandardItemModel):
    
    def __init__(self, table, column, dfilter, *args, **kwargs):
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        self.rcount = None
        self._table = table # TODO: Test that the column is a categorical attribute 
        self._column = column
        
        self._dfilter = dfilter # Could be shared with other condition providers

        self._data = sorted(self._table.distinct(self._column))
        
        for d in self._data:
            item = QtGui.QStandardItem(str(d))
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked)
            item._value = d # if the category is an integer 'item.text()' -> BAD  
            self.appendRow(item)
        
        self.itemChanged.connect(self.on_item_changed)
        
    def update_condition(self):
        filtered_categories = []
        for i in xrange(self.rowCount()):
            item = self.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                filtered_categories.append(item._value) 

        if ( len(filtered_categories) == self.rowCount()
             and self._dfilter.has_condition(self._column) ):
            self._dfilter.remove_condition(self._column)
        else:
            query = {self._column: {'$in':filtered_categories}}
            # TODO: Get lazzy: The next query execution should be done when required 
            result = self._table.find(query, {self._table.index : True}).get_data('c_list')
            ref = result.get(self._table.index, [])
            self._dfilter.set_item_condition(self._column, ref, query)
        
        

    def on_item_changed(self, item):
        self.update_condition()

    
if __name__ == '__main__':
    def print_dfilter(topic, msg):
        #print msg
        #print dfilter.reference
        print dfilter.query
        
    import data_adquisition
    app = QtGui.QApplication([])
    view = CategoricalFilterView('dendrite_id', None)
    table = data_adquisition.create_spines_table()
    dfilter = DynFilter('f_dendrites', table)
    dfilter.subscribe('change', print_dfilter)
    
    model = CategoricalFilterItemModel(table, 'dendrite_id', dfilter)
    view.view.setModel(model)
    view.show()
    item = model.item(0)
    item.setCheckState(QtCore.Qt.Unchecked)
    item.setCheckState(QtCore.Qt.Checked)
    app.exec_()
