import sys

from twisted.internet import reactor
from twisted.python import log

from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol, \
                               listenWS


class EchoServerProtocol(WebSocketServerProtocol):

   def onMessage(self, msg, binary):
      print "sending echo:", msg
      self.sendMessage(msg, binary)


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   factory = WebSocketServerFactory("ws://localhost:9000", debug = False)
   factory.protocol = EchoServerProtocol
   listenWS(factory)

   reactor.run()
