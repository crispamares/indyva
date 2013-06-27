#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Jun 27, 2013

@author: crispamares
'''

from PyQt4 import QtGui, QtCore
import sys
from dataset import RSC_DIR
import json
from collections import OrderedDict
import pandas as pn
from dataset.table import Table
from tabular_view import TabularView

def setUpData():
    df = pn.read_csv(RSC_DIR+'/census.csv')
    with open(RSC_DIR+'/schema_census') as f:
        schema = json.loads(f.read())
    
    schema = OrderedDict(attributes = schema['attributes'], index = schema['index'])
    table = Table('census', schema).data(df)
    return table 


if __name__ == '__main__':
    print'running...'
    app = QtGui.QApplication(sys.argv)
    
    main_window = QtGui.QMainWindow()
    splitter = QtGui.QSplitter(main_window);

    tv = TabularView(main_window)
    tv.set_table(setUpData())
    tv.render_table()

    splitter.addWidget(tv)
    main_window.resize(1000, 700)
    main_window.setCentralWidget(splitter)

    main_window.show()
    app.exec_()