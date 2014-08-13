#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Oct 24, 2013

@author: crispamares
'''

def main_zmq():
    from facade.server import ZMQServer
    
    server = ZMQServer()        
    server.serve_forever()

def main_http():
    from facade.server import WSGIServer
    
    server = WSGIServer()        
    server.serve_forever()

def main_ws():
    from facade.server import WSServer
    
    server = WSServer()        
    server.serve_forever()
    
def main_zmq_and_ws():
    import gevent
    from facade.server import ZMQServer
    from facade.server import WSServer
    zmq_server = ZMQServer()            
    ws_server = WSServer()        
    
    gevent.joinall([zmq_server.start(), ws_server.start()])
    
    

def main2():
    
    from PyQt4 import QtGui
    from external import qtgevent
    qtgevent.install() 
    import gevent
    from gevent import monkey; monkey.patch_all()
    import time
    
    def test_greenlet(name):
        i = 1
        while True:
            print name, i
            i += 1
            time.sleep(1)
    
    def btn_clicked():
        gevent.spawn(test_greenlet, "C")
    
    if __name__ == '__main__':
        app = QtGui.QApplication([])
        mainwin = QtGui.QMainWindow()
        btn = QtGui.QPushButton('Start greenlet', mainwin)
        btn.clicked.connect(btn_clicked)
        gevent.spawn(test_greenlet, 'A')
        gevent.spawn(test_greenlet, 'B')
        
        mainwin.show()
        app.exec_()



def main():    
    import sys
    from PyQt4 import QtGui, Qt
    
    from eventloop import QtLoop, ZMQLoop
    from kernel import Kernel
    from epubsub.hub import Hub
    
    import zmq
    from zmq.eventloop.zmqstream import ZMQStream 
    

    
    def callback(stream, msg):
        print msg
        stream.send('OK')
        
    print 'running'
    #app = QtGui.QApplication(sys.argv)

    loop = ZMQLoop()
    loop.install()
    kernel = Kernel()
    
    ctx = zmq.Context()
    socket = ctx.socket(zmq.ROUTER)
    socket.bind('tcp://127.0.0.1:11111')
    stream = ZMQStream(socket)
    
    stream.on_recv_stream(callback)
    loop.start()
    
    #app.exec_()

if __name__ == '__main__':
    main_zmq_and_ws()