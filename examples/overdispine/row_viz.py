# -*- coding: utf-8 -*-
'''
Created on 04/09/2013

@author: jmorales
'''
from PyQt4 import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class RowViz(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.f = FigureCanvas(Figure(figsize=(8,1)))
        self.ax_1 = self.f.figure.add_subplot(141)
        self.ax_2 = self.f.figure.add_subplot(142)
        self.ax_3 = self.f.figure.add_subplot(143)
        self.ax_4 = self.f.figure.add_subplot(144)
        self.ax_1.hist([1,1,1,1,3,3,3,4,5,7,7,7,7])
        self.ax_2.hist([1,1,1,1,3,3,3,4,5,7,7,7,7])
        self.ax_3.hist([1,1,1,1,3,3,3,4,5,7,7,7,7])
        self.ax_4.hist([1,1,1,1,3,3,3,4,5,7,7,7,7])

    def get_plot(self):
        self.f.setMinimumHeight(120)
        self.f.setSizePolicy(Qt.QSizePolicy.Preferred, Qt.QSizePolicy.Preferred)
        self.f.updateGeometry()
        return self.f
    
    
    