# -*- coding: utf-8 -*-
'''
Created on 04/09/2013

@author: jmorales
'''
from PyQt4 import Qt, QtGui, QtSvg, QtCore
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from collections import OrderedDict

import StringIO

from indyva.epubsub import hub


class RowSVGViz(QtSvg.QSvgWidget):

    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        self._dselect = None
        self._selection = None
        
        QtSvg.QSvgWidget.__init__(self, *args)
        self.setMinimumHeight(220)
        self.setSizePolicy(Qt.QSizePolicy.Preferred, Qt.QSizePolicy.Preferred)
        
        self.figure = plt.figure(figsize=(16,3), facecolor='r')
        
        self.ax_1 = self.figure.add_subplot(141, title='points')
        self.ax_2 = self.figure.add_subplot(142, title='size')
        self.ax_3 = self.figure.add_subplot(143, title='length')
        self.ax_4 = self.figure.add_subplot(144, title='angle')

        self._spines = None
        self.dendrite_id = ''
        
        self.dirty = False
        self.selected = False

    @property
    def dselect(self):
        return self._dselect
    @dselect.setter
    def dselect(self, dselect):
        '''
        :param DynSelect dselect: 
        '''
        self._dselect = dselect
        self._dselect.subscribe('change', self.on_dselect_change)
        
    def on_render(self, topic, msg):
        self.update_view()

    def on_dselect_change(self, topic, msg):
        now_selected = self.dendrite_id in self.dselect.reference
        if now_selected and not self.selected:        
            self.selected = True
            self.dirty = True
        elif self.selected and not now_selected:
            self.selected = False
            self.dirty = True
        #self.update_view()

    def mousePressEvent( self, event ):
        #print "Click with dselect:", self.dselect
        if not self.dselect:
            return
        self._selection = self.dselect.get_condition('s_dendrite_id', None)
        if self._selection is None:
            self._selection = self.dselect.new_categorical_condition(
                'dendrite_id', name='s_dendrite_id') 
           
        self._selection.exclude_all()
        self._selection.add_category(self.dendrite_id)
        #print 'selected:', self._selection.included_items()
        #self.dselect.update(self._selection)
        
    @property
    def spines(self):
        return self._spines
    
    @spines.setter
    def spines(self, spines):
        self._spines = spines
        self.dirty = True
        
    def update_view(self):
        if self.spines is None:
            raise Exception('No spines assigned before painting')
        if not self.dirty:
            return
        
        facecolor='r' if self.selected else 'w'
        
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
        
        imgdata = StringIO.StringIO()
        self.figure.savefig(imgdata, format='svg', facecolor=facecolor)
        imgdata.seek(0)  # rewind the data
        svg = imgdata.read()
        self.load(QtCore.QByteArray( svg ))

        self.dirty = False
        

class VizListView(object):
    
    def __init__(self, table=None, dfilter=None, dselect=None):
        self.table = table
        self._dfilter = dfilter
        self._dselect = dselect
        self.plots = OrderedDict()
        
        self.dirty = True

        self.scroll = QtGui.QScrollArea()
        
        self.viz_area = QtGui.QWidget(self.scroll)
        self.v_layout = QtGui.QVBoxLayout(self.viz_area)
        #self.v_layout.setSizeConstraint(self.v_layout.SetNoConstraint)
        self.scroll.setBackgroundRole(Qt.QPalette.Dark)
        self.scroll.setWidget(self.viz_area)
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(2)
    
        hub.instance().subscribe('r:', self.on_render)
    
    @property
    def dfilter(self):
        return self._dfilter
    @dfilter.setter
    def dfilter(self, dfilter):
        '''
        :param DynSelect dfilter: 
        '''
        self._dfilter = dfilter 
        self._dfilter.subscribe('change', self.on_dfilter_change)
    @property
    def dselect(self):
        return self._dselect
    @dselect.setter
    def dselect(self, dselect):
        self._dselect = dselect 
        for plot in self.plots.values():
            plot.dselect = dselect
        
    def on_dfilter_change(self, topic, msg):
        self.dirty = True
    
    @property
    def widget(self):
        return self.scroll
    
    def add_plot(self, name, plot):
        self.plots[name] = plot
        plot.setObjectName('_plot_'+name)
        self.v_layout.addWidget(plot)
        plot.update_view()
        
    def show_plot(self, name):
        self.plots[name].setVisible(True)
        
    def hide_plot(self, name):
        self.plots[name].hide()
        
    def on_render(self, topic, msg):
        for plot in self.plots.values():
            plot.on_render(topic, msg)
        if self.dirty:
            self.dirty = False
            self.update_view()
        
    
    def update_view(self):
        if self.table is None:
            raise Exception('No table assigned before painting')
        
        if self.dfilter is not None:
            dendrites = sorted(self.dfilter.reference)    
        else:
            dendrites = sorted(self.table.distinct('dendrite_id'))        

        print 'dendrites', dendrites
        print '++ dfilter', self.dfilter

        plots_to_remove = set(self.plots.keys()).difference(dendrites)
        print 'plots-to-remove', plots_to_remove
        for name in plots_to_remove:
            #print 'removing', name
            self.hide_plot(name)
        
        for dendrite in dendrites:
            if dendrite in self.plots:
                if not self.plots[dendrite].isVisible():
                    self.show_plot(dendrite)
                #print 'Yet ploted', dendrite
                continue

            #print 'ADDING', dendrite
            v_spines = self.table.find({'dendrite_id':dendrite},
                                       {'unroll_pos':True,
                                        'size':True,
                                        'length':True,
                                        'angle':True})
            spines = v_spines.get_data('c_list')
            
            plot = RowSVGViz()
            plot.spines = spines
            plot.dselect = self._dselect
            plot.dendrite_id = dendrite
            self.add_plot(dendrite, plot)
            self.dirty = True
            return
        print 'FINISH'

    