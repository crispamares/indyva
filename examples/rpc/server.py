# -*- coding: utf-8 -*-
'''
Created on 18/07/2013

@author: jmorales
'''

import loop
from facade import endpoint, front

class Echoer(front.IService):
    def echo(self, a):
        return a
    
    
def main():
    print 'running'
    e = endpoint.Endpoint()
    Echoer('echoer')
    e.run()
    
    l = loop.Loop
    l.run()
    print 'stop'
if __name__ == '__main__':
    main()