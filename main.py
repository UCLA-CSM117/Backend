#!/usr/bin/python

import blast.messagequeue
from twisted.internet import protocol, reactor, endpoints


queue = blast.messagequeue.MessageQueue(1000)

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        try:
            print data
            if(data.beginsWith("GETMESSAGES")):
                self.transport.write(queue.getRecentsString())
            else:
                queue.pushMessage(Message.fromString(data))
                self.transport.write("OK")
        except Exception as e:
            self.transport.write("FAIL")
        self.transport.loseConnection()

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

if(__name__ == '__main__'):
    endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
    reactor.run()
