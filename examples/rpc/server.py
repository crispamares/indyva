# -*- coding: utf-8 -*-
'''
Created on 18/07/2013

@author: jmorales
'''


from indyva.kernel import Kernel
from indyva.facade.server import ZMQServer



def main():
    zmq_server = ZMQServer(10111)
    kernel = Kernel()
    kernel.add_server(zmq_server)

    print 'running'    
    print kernel.run_forever()
    print 'stop'
    
if __name__ == '__main__':
    main()