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
        self.need_draw = False

    @property
    def dselect(self):
        return self._dselect
    @dselect.setter
    def dselect(self, dselect):
        '''
        :param DynSelect dselect: 
        '''
        self._dselect = dselect #### TODO: Continue here
        self._dselect.subscribe('change', self.on_dselect_change)

    def on_dselect_change(self, topic, msg):
        self.update_view()

    def mousePressEvent( self, event ):
        print "Click with dselect:", self.dselect
        if not self.dselect:
            return
        self._selection = self.dselect.get_condition('s_dendrite_id', None)
        if self._selection is None:
            self._selection = self.dselect.new_categorical_condition(
                'dendrite_id', name='s_dendrite_id') 
        
        self.need_draw = True    
        self._selection.exclude_all()
        self.need_draw = True    
        self._selection.add_category(self.dendrite_id)
        print 'selected:', self._selection.included_items()
        #self.dselect.update(self._selection)
        
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
        
        facecolor='b'
        if self.dselect:
            selection = self.dselect.get_condition('s_dendrite_id', None)
            if selection is not None: 
                print '** font_color', selection.included_items()
                if self.dendrite_id in selection.included_items():
                    facecolor = 'r'
        
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
        
        
        self.need_draw = False
        

class VizListView(object):
    
    def __init__(self, table=None, dfilter=None, dselect=None):
        self.table = table
        self._dfilter = dfilter
        self._dselect = dselect
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
        
    def on_dfilter_change(self, topic, msg):
        self.update_view()    
    
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
        print 'FINISH'

    