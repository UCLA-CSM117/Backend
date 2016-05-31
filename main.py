#!/usr/bin/python

import blast.messagequeue
import blast.user
from twisted.internet import protocol, reactor, endpoints
import json
import traceback

queue = blast.messagequeue.MessageQueue(1000)

"""
{"request": "NEWTOKEN", "nickname", "nick"} --> {"status": "OK", "token" : "1234"}
{"request": "NEWMESSAGES", "time": <utc timestamp>, "token", "1234"} --> {"status": "OK", "messages" : [{...}, {...}, ...]}
{"request": "SENDMESSAGE", "message": {...}} --> {"status": "OK"}
{"request": "NEARBYTOKENS", "token": "1234", "nearby_tokens": ["1235", ...]} --> {"status": "OK"}
"""

userGraph = blast.user.UserGraph()

def merge_dicts(*dict_args):
    result = dict()
    for d in dict_args:
        result.update(d)
    return result

def failResponse(response_dict = {}):
    return merge_dicts({"status":"FAIL"}, response_dict)

def okResponse(response_dict = {}):
    return merge_dicts({"status":"OK"}, response_dict)

def handleNewToken(request_object):
    request = request_object["request"]
    nickname = request_object["nickname"]

    try:
        userGraph.getUserByNickname(nickname)
        return failResponse({"reason": e.message})
    except Exception as e:
        pass

    newuser = userGraph.addUserByNickname(nickname)
    token = newuser.token

    return okResponse({"token": token})

def handleNewMessages(request_object):
    timestamp = request_object["timestamp"]
    token = request_object["token"]

    user = userGraph.getUserByToken(int(token))
    user_queue = user.getQueue()
    messages = user_queue.getRecents(timestamp)
    return okResponse({"messages": messages})

def handleSendMessage(request_object):
    message = request_object["message"]
    message_object = blast.messagequeue.Message(message["message"],
                                                message["token"],
                                                message["nickname"],
                                                message["timestamp"])

    if userGraph.pushMessage(message_object):
        return okResponse()
    return failResponse()

def handleNearbyTokens(request_object):
    token = request_object["token"]
    nearby_tokens = request_object["nearby_tokens"]

    if None in nearby_tokens:
        print "Client sent null nearby tokens: ", nearby_tokens
    nearby_tokens = filter(lambda x : not x == None, nearby_tokens)

    user = userGraph.getUserByToken(token)
    neaby_users = map(userGraph.getUserByToken, nearby_tokens)

    userGraph.updateConnections(user, neaby_users)

    return okResponse()

def processRequestString(request_string):
    request_object = json.loads(request_string)
    request = request_object["request"]

    response_object = \
    {"NEWTOKEN" : handleNewToken,
     "NEWMESSAGES" : handleNewMessages,
     "SENDMESSAGE" : handleSendMessage,
     "NEARBYTOKENS" : handleNearbyTokens
    }[request](request_object)

    return json.dumps(merge_dicts(response_object, {"request": request}))

def failString():
    return json.dumps(failResponse())

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        try:
            print "GOT: %s" % data
            response = (processRequestString(data))
            print "SENDING: %s" % response
            self.transport.write(response)
        except Exception as e:
            self.transport.write(json.dumps(failResponse({"reason":e.message})))

            traceback.print_exc()
            print "FAILED: %s" % e.message
        self.transport.loseConnection()

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

if(__name__ == '__main__'):
    endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
    reactor.run()
