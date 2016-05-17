import json

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
