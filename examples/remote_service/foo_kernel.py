# -*- coding: utf-8 -*-
'''
Created on 09/12/2013

@author: jmorales
'''
import gevent

from indyva.kernel import Kernel
from indyva.facade.server import ZMQServer
zmq_server = ZMQServer(8090)
kernel = Kernel()
kernel.add_server(zmq_server)

print 'running -- '     
server = kernel.start()

def call_now():
    while True:
        try:
            response = zmq_server.dispatcher.get_method('DateSrv.now')()
            print '-->', response
        except Exception, e:
            print '** Error:', e
        gevent.sleep(3)
        
c = gevent.spawn(call_now)

gevent.joinall(server + [c])
    


