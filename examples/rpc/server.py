# -*- coding: utf-8 -*-
'''
Created on 18/07/2013

@author: jmorales
'''

import loop
from facade import endpoint, front

def main():
    print 'running'
    e = endpoint.Endpoint()
    e.run()
    
    l = loop.Loop
    l.run()
    print 'stop'
if __name__ == '__main__':
    main()