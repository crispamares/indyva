# -*- coding: utf-8 -*-
'''
Created on 03/09/2013

@author: jmorales
'''
import sys
from PyQt4 import QtGui, Qt

from row_viz import VizListView
import data_adquisition
from filters_ui import CategoricalFilterView, CategoricalFilterItemModel
from dynamics.dfilter import DynFilter
from dynamics.dselect import DynSelect


__version__ = '0.1'

class MainWindow(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        QtGui.QMainWindow.__init__(self, *args, **kwargs)
        self.build_gui()

    def build_gui(self):
        self.resize(1000, 700)
        self.setWindowTitle('OverDispine '+ __version__)

        self.list_view = VizListView()
        self.setCentralWidget(self.list_view.widget)

    def add_filter(self, table, column, dfilter):
        model = CategoricalFilterItemModel(table, column, dfilter)
        fview = CategoricalFilterView(column, self)
        fview.view.setModel(model)
        
        self.addDockWidget(Qt.Qt.RightDockWidgetArea, fview.get_in_dock(self))        

def main():
    app = QtGui.QApplication(sys.argv)
    
    table = data_adquisition.create_table()
        
    main_window = MainWindow()
    main_window.show()

    view = main_window.list_view

    dfilter = DynFilter('f_dendrites')
    main_window.add_filter(table, 'dendrite_id', dfilter)
    main_window.add_filter(table, 'dendrite_type', dfilter)
    #main_window.add_filter(table, 'section', dfilter)
    dfilter.subscribe('change', lambda t,m : view.update_view())
    dfilter.subscribe('remove', lambda t,m : view.update_view())



    dselect = DynSelect('s_dendrites', 'OR')
    
    view.table = table
    view.dfilter = dfilter
    view.dselect = dselect
    view.update_view()
    
    

    app.exec_()
    

if __name__ == '__main__':
    main()
    print 'end'