# -*- coding: utf-8 -*-
'''
Created on 03/09/2013

@author: jmorales
'''
import sys
from collections import OrderedDict

from PyQt4 import QtGui, Qt

from row_viz import RowViz
import data_adquisition


__version__ = '0.1'

class MainWindow(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        QtGui.QMainWindow.__init__(self, *args, **kwargs)

        self.plots = OrderedDict()

        self.build_gui()

    def add_plot(self, name, plot):
        self.plots[name] = plot
        plot.setObjectName('_plot_'+name)

    def remove_plot(self, name):
        self.plots.pop(name)
        
    def render_plots(self):
        # insert plots
        for i, name in enumerate(self.plots):
            child = self.viz_area.findChild(QtGui.QLabel, name='_plot_'+name)
            if child is None:
                self.v_layout.insertWidget(i, self.plots[name])
        # remove plots
        children_plots = { str(o.objectName()).replace('_plot_', '') : o 
                          for o in self.viz_area.children() 
                          if str(o.objectName()).startswith('_plot_')}
        plots_to_remove = set(children_plots.keys()).difference(self.plots.keys())
        
        for plot in plots_to_remove:
            self.v_layout.removeWidget(children_plots[plot])
            children_plots[plot].deleteLater()
        
        self.scroll.adjustSize()
        
    def build_gui(self):
        self.resize(1000, 700)
        self.setWindowTitle('OverDispine '+ __version__)

        #self.v_layout.setSizeConstraint(self.v_layout.SetMinAndMaxSize)

        self.scroll = QtGui.QScrollArea(self.centralWidget())
        
        self.viz_area = QtGui.QWidget(self.scroll)
        self.v_layout = QtGui.QVBoxLayout(self.viz_area)
        #self.v_layout.setSizeConstraint(self.v_layout.SetNoConstraint)
        self.scroll.setBackgroundRole(Qt.QPalette.Dark)
        self.scroll.setWidget(self.viz_area)
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(2)

        self.setCentralWidget(self.scroll)
        

def main():
    app = QtGui.QApplication(sys.argv)
    
    main_window = MainWindow()
    main_window.show()


        
    main_window.add_plot('lpaco1', QtGui.QLabel('paco label', main_window))
    main_window.add_plot('lpaco3', QtGui.QLabel('paco label 3', main_window))
    main_window.add_plot('lpaco2', QtGui.QLabel('paco label 2', main_window))
    for i in range(70):
        r = RowViz()
        main_window.add_plot('paco{}'.format(i), r.get_plot())
    main_window.render_plots()

    
    #main_window.scroll.widget().resize(300, 300)
    

    print r.get_plot()
    app.exec_()
    

if __name__ == '__main__':
    main()
    print 'end'