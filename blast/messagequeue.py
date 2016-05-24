import json

class Message(object):
    def __init__(self, message, token, nickname, timestamp):
        """Initializes a new Message object"""
        self.message = message
        self.token = token
        self.nickname = nickname
        self.timestamp = timestamp

    def moreRecent(self, timestamp):
        """Determines if the Message is more recent than the given UTC
        timestamp"""
        return (self.timestamp <= timestamp)

    def toString(self):
        """Serializes a Message to a JSON string"""
        return  json.dumps({'message': self.message, 'nickname': self.nickname,
                            'token': self.token, 'timestamp' : self.timestamp})

    @staticmethod
    def json_object_hook(data):
        return Message(data["message"], data["token"], data["nickname"],
                       data["timestamp"])

    @staticmethod
    def fromString(s):
        """Deserializes a Message from a JSON string"""
        return json.loads(s, object_hook=json_object_hook)

class MessageQueue(object):
    def __init__(self, depth):
        """Initializes a new MessageQueue object"""
        self.messages = set()
        self.depth = depth

    def getRecents(self, lastTimestamp, flush=True):
        recents = set(filter(lambda x : x.moreRecent(lastTimestamp), self.messages))
        messages = self.messages.difference(recents)
        return recents

    def getRecentsString(self, lastTimestamp):
        return "[" + ",".join([x.toString() for x in self.getRecents(lastTimestamp)]) + "]"

    def pushMessage(self, message):
        """Pushes a new Message onto the queue. If the queue is full, returns
        False; otherwise, returns True."""
        if(len(self.messages) < self.depth):
            self.messages.add(message)
            return True
        return False
