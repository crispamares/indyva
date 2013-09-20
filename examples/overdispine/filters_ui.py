# -*- coding: utf-8 -*-
'''
Created on 20/09/2013

@author: jmorales
'''
from PyQt4 import QtGui, QtCore

class CategoricalFilterView(QtGui.QListView):
    '''
    This class provide a filter menu for categorical column 
    '''

    def __init__(self, *args, **kwargs):
        QtGui.QListView.__init__(self, *args, **kwargs)

        
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
    
    def __init__(self, table, column, *args, **kwargs):
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        self.rcount = None
        self._table = table # TODO: Test that the column is a categorical attribute 
        self.selection = None
        self._column = column

        self._data = sorted(self._table.distinct(self._column))
        
        for d in self._data:
            item = QtGui.QStandardItem(d)
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked)
            self.appendRow(item)
        
        self.itemChanged.connect(self.on_item_changed)
    
    def on_item_changed(self, item):
        # If the changed item is not checked, don't bother checking others
        if item.checkState() == QtCore.Qt.Checked:
            print item.text(), 'checked'     

    
if __name__ == '__main__':
    import data_adquisition
    app = QtGui.QApplication([])
    view = CategoricalFilterView(None)
    table = data_adquisition.create_table()
    model = CategoricalFilterItemModel(table, 'dendrite_id')
    view.setModel(model)
    view.show()
    item = model.item(0)
    item.setCheckState(QtCore.Qt.Unchecked)
    item.setCheckState(QtCore.Qt.Checked)
    app.exec_()
