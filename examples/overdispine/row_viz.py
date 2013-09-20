# -*- coding: utf-8 -*-
'''
Created on 04/09/2013

@author: jmorales
'''
from PyQt4 import Qt, QtGui
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from collections import OrderedDict



class RowViz(FigureCanvas):
    '''
    classdocs
    '''
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        FigureCanvas.__init__(self, Figure((8,3)))
        self.setMinimumHeight(220)
        self.setSizePolicy(Qt.QSizePolicy.Preferred, Qt.QSizePolicy.Preferred)
        self.updateGeometry()

        self.ax_1 = self.figure.add_subplot(141, title='points')
        self.ax_2 = self.figure.add_subplot(142, title='size')
        self.ax_3 = self.figure.add_subplot(143, title='length')
        self.ax_4 = self.figure.add_subplot(144, title='angle')

        self.spines = None
        self.dendrite_id = ''

    def mousePressEvent( self, event ):
        print "Click"
        
    def update_view(self):
        if self.spines is None:
            raise Exception('No spines assigned before painting')
        
        print self.dendrite_id
        self.figure.suptitle(self.dendrite_id)        
        
        try:
            #self.ax_1.hist([1,1,1,1,3,3,3,4,5,7,7,7,7])
            self.ax_2.hist(self.spines['size'])
            self.ax_3.hist(self.spines['length'])
            self.ax_4.hist(self.spines['angle'])
        except Exception, e:
            QtGui.QMessageBox.warning(None, 'Painting ' + self.dendrite_id,
                                           str(e) )
        
        self.figure.tight_layout()
        
    def update(self):
        self.figure.tight_layout()
        FigureCanvas.update(self)

class ListView(object):
    
    def __init__(self, table=None):
        self.table = table
        self.plots = OrderedDict()

        self.scroll = QtGui.QScrollArea()
        
        self.viz_area = QtGui.QWidget(self.scroll)
        self.v_layout = QtGui.QVBoxLayout(self.viz_area)
        #self.v_layout.setSizeConstraint(self.v_layout.SetNoConstraint)
        self.scroll.setBackgroundRole(Qt.QPalette.Dark)
        self.scroll.setWidget(self.viz_area)
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(2)
    
    @property
    def widget(self):
        return self.scroll
    
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
                plot = self.plots[name]
                self.v_layout.insertWidget(i, plot)
                if isinstance(plot, RowViz): plot.update_view()
        # remove plots
        children_plots = { str(o.objectName()).replace('_plot_', '') : o 
                          for o in self.viz_area.children() 
                          if str(o.objectName()).startswith('_plot_')}
        plots_to_remove = set(children_plots.keys()).difference(self.plots.keys())
        
        for plot in plots_to_remove:
            self.v_layout.removeWidget(children_plots[plot])
            children_plots[plot].deleteLater()
        
        self.scroll.adjustSize()
        
    
    def update_view(self):
        if self.table is None:
            raise Exception('No table assigned before painting')
            
        dendrites = sorted(self.table.distinct('dendrite_id'))
        
        for dendrite in dendrites:
            v_spines = self.table.find({'dendrite_id':dendrite},
                                       {'unroll_pos':True,
                                        'size':True,
                                        'length':True,
                                        'angle':True})
            spines = v_spines.get_data('c_list')
            
            plot = RowViz()
            plot.spines = spines
            plot.dendrite_id = dendrite
            self.add_plot(dendrite, plot)
        
        self.render_plots()
    