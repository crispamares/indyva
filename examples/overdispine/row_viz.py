# -*- coding: utf-8 -*-
'''
Created on 04/09/2013

@author: jmorales
'''
from PyQt4 import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas



class RowViz(FigureCanvas):
    '''
    classdocs
    '''
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        FigureCanvas.__init__(self, Figure(figsize=(8,1)))
        self.setMinimumHeight(120)
        self.setSizePolicy(Qt.QSizePolicy.Preferred, Qt.QSizePolicy.Preferred)
        self.updateGeometry()

        self.ax_1 = self.figure.add_subplot(141)
        self.ax_2 = self.figure.add_subplot(142)
        self.ax_3 = self.figure.add_subplot(143)
        self.ax_4 = self.figure.add_subplot(144)
        
    def render(self):
        self.ax_1.hist([1,1,1,1,3,3,3,4,5,7,7,7,7])
        self.ax_2.hist([1,1,1,1,3,3,3,4,5,7,7,7,7])
        self.ax_3.hist([1,1,1,1,3,3,3,4,5,7,7,7,7])
        self.ax_4.hist([1,1,1,1,3,3,3,4,5,7,7,7,7])

    
    