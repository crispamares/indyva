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

        self._spines = None
        self.dendrite_id = ''
        self.need_draw = False

    def mousePressEvent( self, event ):
        print "Click"
        
    @property
    def spines(self):
        return self._spines
    
    @spines.setter
    def spines(self, spines):
        self._spines = spines
        self.need_draw = True
        
    def update_view(self):
        if self.spines is None:
            raise Exception('No spines assigned before painting')
        if not self.need_draw:
            return
        
        print 'update-view', self.dendrite_id
        self.figure.suptitle(self.dendrite_id)        
        
        try:
            #self.ax_1.hist([1,1,1,1,3,3,3,4,5,7,7,7,7])
            self.ax_2.hist(self.spines['size'])
            self.ax_3.hist(self.spines['length'])
            self.ax_4.hist(self.spines['angle'])
        except Exception, e:
            #QtGui.QMessageBox.warning(None, 'Painting ' + self.dendrite_id, str(e) )
            print 'Error', e
        #self.figure.tight_layout()

        self.need_draw = False
        

class VizListView(object):
    
    def __init__(self, table=None, dfilter=None):
        self.table = table
        self.dfilter = dfilter
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

        # remove plots
        children_plots = { str(o.objectName()).replace('_plot_', '') : o 
                          for o in self.viz_area.children() 
                          if str(o.objectName()).startswith('_plot_')}
        plots_to_remove = set(children_plots.keys()).difference(self.plots.keys())
        print 'REALLY plots to remove', plots_to_remove
        for plot in plots_to_remove:
            self.v_layout.removeWidget(children_plots[plot])
            children_plots[plot].deleteLater()
        
        # Update plots
        for plot in self.plots.values():
            plot.update_view()
        
        print 'finshing update'
        #self.scroll.adjustSize()
        self.viz_area.update()
        print 'finished update'
        
    
    def update_view(self):
        if self.table is None:
            raise Exception('No table assigned before painting')
        query = {}
        if self.dfilter is not None:
            query, _ = self.dfilter.query('spine_id')
        print query 
        dendrites = sorted(self.table.find(query).distinct('dendrite_id'))        
        #
        plots_to_remove = set(self.plots.keys()).difference(dendrites)
        print 'plots-to-remove', plots_to_remove
        for name in plots_to_remove:
            print 'removing', name
            self.remove_plot(name)
        
        for dendrite in dendrites:
            if self.plots.has_key(dendrite):
                print 'Yet ploted', dendrite
                continue

            #print 'ADDING', dendrite
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
    