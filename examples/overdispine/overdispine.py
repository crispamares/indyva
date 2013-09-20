# -*- coding: utf-8 -*-
'''
Created on 03/09/2013

@author: jmorales
'''
import sys
from collections import OrderedDict

from PyQt4 import QtGui, Qt

from row_viz import RowViz, ListView
import data_adquisition


__version__ = '0.1'

class MainWindow(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        QtGui.QMainWindow.__init__(self, *args, **kwargs)



        self.build_gui()

        
    def build_gui(self):
        self.resize(1000, 700)
        self.setWindowTitle('OverDispine '+ __version__)

        self.list_view = ListView()
        self.setCentralWidget(self.list_view.widget)
        

def main():
    app = QtGui.QApplication(sys.argv)
    
    main_window = MainWindow()
    main_window.show()

    view = main_window.list_view

    view.add_plot('lpaco1', QtGui.QLabel('paco label', main_window))
    view.add_plot('lpaco3', QtGui.QLabel('paco label 3', main_window))
    view.add_plot('lpaco2', QtGui.QLabel('paco label 2', main_window))

    table = data_adquisition.create_table()
    view.table = table
    view.update_view()
    
    #main_window.scroll.widget().resize(300, 300)

    app.exec_()
    

if __name__ == '__main__':
    main()
    print 'end'