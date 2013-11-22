# -*- coding: utf-8 -*-
'''
Created on 18/07/2013

@author: jmorales
'''


from kernel import Kernel
from facade.server import ZMQServer



def main():
    zmq_server = ZMQServer(10111)
    kernel = Kernel()
    zmq_server.start()

    print 'running'    
    print kernel.run_forever()
    print 'stop'
    
if __name__ == '__main__':
    main()