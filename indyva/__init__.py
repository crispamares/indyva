# -*- coding: utf-8 -*-
'''
Created on 11/12/2013

:author: jmorales

Indyva (Interactive Dynamics for Visual Analytics) project
'''

__version__ = '0.1.1'


# Some auxiliary functions that should be provided by external
# libraries They are somehow hidden here, so I don't need an "utils"
# module which I don't like.
def for_json_bridge(o):
    try:
        return o.for_json()
    except AttributeError:
        raise TypeError('{0} is not JSON serializable'.format(o))
