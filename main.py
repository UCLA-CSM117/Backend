#!/usr/bin/python

from twisted.internet import protocol, reactor, endpoints
import json

class User(object):
    def __init__(self, nick):
        self.nick = nick
        self.adjacents = []

class Message(object):
    def __init__(self, msg, msgid, timestamp):
        self.msg = msg
        self.id = msgid
        self.time = timestamp

    def moreRecent(self, timestamp):
        return (self.time <= timestamp)

    def toString(self):
        return  json.dumps({'msg': self.msg, 'nick': self.nick, 'id': self.id, 'time' : self.time})

    @staticmethod
    def fromString(s):
        return json.loads(s, object_hook=lambda d : Message(d['msg'], d['id'], d['time']))

class MessageQueue(object):
    def __init__(self, depth):
        self.msgs = []
        self.depth = depth

    def getRecents(lastTimestamp):
        return filter(lambda x : x.moreRecent(lastTimestamp), self.msgs)

    def getRecentsString(lastTimestamp):
        return "[" + ",".join(getRecents(lastTimestamp)) + "]"

    def pushMessage(self, msg):
        self.msgs.append(msg)

queue = MessageQueue(1000)

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        try:
            if(data.beginsWith("GETMESSAGES: ")):
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
