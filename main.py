#!/usr/bin/python

import blast.messagequeue
import blast.user
from twisted.internet import protocol, reactor, endpoints
import json

queue = blast.messagequeue.MessageQueue(1000)

"""
{"request": "NEWTOKEN", "nickname", "nick"} --> {"status": "OK", "token" : "1234"}
{"request": "NEWMESSAGES", "time": <utc timestamp>, "token", "1234"} --> {"status": "OK", "messages" : [{...}, {...}, ...]}
{"request": "SENDMESSAGE", "message": {...}} --> {"status": "OK"}
{"request": "NEARBYTOKENS", "token": "1234", "nearby_tokens": ["1235", ...]} --> {"status": "OK"}
"""

userGraph = blast.user.UserGraph()

def handleNewToken(request_object):
    request = request_object["request"]
    nickname = request_object["nickname"]

    token = userGraph.addUserByNickname(nickname)

    return json.dumps({"request": request, "status": "OK", "token": token})

def handleNewMessages(request_object):
    timestamp = request_object["timestamp"]
    token = request_object["token"]
    messages = [] #userManager.getUserByToken(token).getQueue().getRecentsString()
    return json.dumps({"request": request, "status": "OK", "messages": messages})

def handleSendMessage(request_object):
    message = blast.messagequeue.Message.fromString(json.dumps(request_object["message"]))

def processRequestString(request_string):
    request_object = json.loads(request_string)
    print "Request object: ", request_object
    request = request_object["request"]
    print "request: ", request

    response = \
    {"NEWTOKEN" : handleNewToken,
     "NEWMESSAGES" : handleNewMessages,
     "SENDMESSAGE" : handleSendMessage
    }[request](request_object)

    return response

def failString():
    return json.dumps({"status": "FAIL"})

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        try:
            print "GOT: %s" % data
            response = (processRequestString(data))
            print "SENDING: %s" % response
            self.transport.write(response)
        except Exception as e:
            self.transport.write(failString())
        self.transport.loseConnection()

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

if(__name__ == '__main__'):
    endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
    reactor.run()
