# -*- coding: utf-8 -*-
'''
Created on 20/09/2013

@author: jmorales
'''
from PyQt4 import QtGui, QtCore
from indyva.dynamics.dfilter import DynFilter

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
        '''
        :param Table table:
        :param DynFilter dfilter: 
        '''
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        self.rcount = None
        self._table = table # TODO: Test that the column is a categorical attribute 
        self._column = column
        
        self._dfilter = dfilter # Could be shared with other condition providers
        self._categories = sorted(self._table.distinct(self._column))        

        self.condition = dfilter.new_categorical_condition(column, name=column)
        self.condition.include_all()
        included_categories = self.condition.included_categories()
        for d in self._categories:
            item = QtGui.QStandardItem(str(d))
            item.setCheckable(True)
            checked = ( QtCore.Qt.Checked if d in included_categories 
                else QtCore.Qt.UnChecked )
            item.setCheckState(checked)
            item._value = d # if the category is an integer 'item.text()' -> BAD  
            self.appendRow(item)
        
        self.itemChanged.connect(self.on_item_changed)
        dfilter.subscribe('change', self.updated_dfilter)
        dfilter.subscribe('remove', self.updated_dfilter)
        
    def updated_dfilter(self, topic, msg):
        self.itemChanged.disconnect(self.on_item_changed)

        included_categories = self.condition.included_categories()
        for i in xrange(self.rowCount()):
            item = self.item(i)
            d = item._value
            checked = ( QtCore.Qt.Checked if d in included_categories 
                else QtCore.Qt.Unchecked)
            item.setCheckState(checked)

        self.itemChanged.connect(self.on_item_changed)

    def on_item_changed(self, item):
        print '*** on_item_changed'
        if item.checkState() == QtCore.Qt.Checked:
            self.condition.add_category(item._value)
        else:
            self.condition.remove_category(item._value)


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
