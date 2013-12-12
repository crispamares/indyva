#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Jun 27, 2013

@author: crispamares
'''


from PyQt4 import QtGui, Qt
from indyva.external import qtgevent
qtgevent.install()

import sys
from indyva.dataset import RSC_DIR
import json
from collections import OrderedDict
import pandas as pn
from indyva.dataset.table import Table
from tabular_view import TabularView

from internal_ipkernel import InternalIPKernel
from indyva import kernel

class IPWindow(Qt.QWidget, InternalIPKernel):

    def __init__(self, app):
        Qt.QWidget.__init__(self)
        self.app = app
        self.add_widgets()
        self.init_ipkernel('qt')

    def add_widgets(self):
        self.setGeometry(300, 300, 400, 70)
        self.setWindowTitle('IPython in your app')

        # Add simple buttons:
        console = Qt.QPushButton('Qt Console', self)
        console.setGeometry(10, 10, 100, 35)
        self.connect(console, Qt.SIGNAL('clicked()'), self.new_qt_console)

        namespace = Qt.QPushButton('Namespace', self)
        namespace.setGeometry(120, 10, 100, 35)
        self.connect(namespace, Qt.SIGNAL('clicked()'), self.print_namespace)

        # Quit and cleanup
        quit = Qt.QPushButton('Quit', self)
        quit.setGeometry(320, 10, 60, 35)
        self.connect(quit, Qt.SIGNAL('clicked()'), Qt.qApp, Qt.SLOT('quit()'))

        self.app.connect(self.app, Qt.SIGNAL("lastWindowClosed()"),
                         self.app, Qt.SLOT("quit()"))

        self.app.aboutToQuit.connect(self.cleanup_consoles)


def setUpData():
    df = pn.read_csv(RSC_DIR+'/census.csv')
    with open(RSC_DIR+'/schema_census') as f:
        schema = json.loads(f.read())
    
    schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])
    table = Table('census', schema).data(df)
    return table 

def getDF():
    return pn.read_csv(RSC_DIR+'/census.csv')

def test_dselect_and_dfilter(tv):
    from indyva.dynamics.dselect import DynSelect
    d = DynSelect('sel1', tv.table)
    tv.set_highlight(d)
    horizontal2 = d.new_categorical_condition('State', 'horizontal2')
    horizontal2.add_category(['RI','SD', 'NY', 'VT'])
    d.update(horizontal2)

    from indyva.dynamics.dfilter import  DynFilter
    f = DynFilter('filt1', tv.table)
    tv.set_dynfilter(f)
    f.new_categorical_condition('State', ['DC','NY'], 'horizontal')
    f.new_attribute_condition(['State', 'Information'], 'vertical')
    
   
def main():    
    app = QtGui.QApplication(sys.argv)
    
    k = kernel.Kernel()
    k.start()    

            
    ipwin = IPWindow(app)    
    
    main_window = QtGui.QMainWindow()
    splitter = QtGui.QSplitter(main_window);

    tv = TabularView(main_window)
    tv.set_table(setUpData())
    tv.render_table()

    splitter.addWidget(tv)
    main_window.resize(1000, 700)
    main_window.setCentralWidget(splitter)

    main_window.show()
    ipwin.show()
    
    ipwin.namespace['tv'] = tv
    ipwin.namespace['k'] = k
    ipwin.namespace['table'] = tv.table
    ipwin.namespace['getDF'] = getDF
    ipwin.namespace['test_dselect_and_dfilter'] = test_dselect_and_dfilter
    
    
    ipwin.ipkernel.start()
    


if __name__ == '__main__':
    print'running...'
    main()