import random
import blast.messagequeue

class User(object):
    def __init__(self, token, nickname):
        self.token = token
        self.nickname = nickname
        self.adjacents = {}
        self.queue = blast.messagequeue.MessageQueue(100)

    def getQueue(self):
        return self.queue

    def addAdjacents(self, users):
        """Register adjacent users with this user"""
        for user in users:
            self.adjacents[user] = 1.0

    def updateAdjacents(self, users):
        self.adjacents = dict()
        self.addAdjacents(users)

    def getConnected(self, threshold=0.5):
        return self.__getConnected__(threshold, set())

    def __getConnected__(self, threshold, partial):
        adjacents = self.adjacents.keys()
        new_adjacents = set()

        for user in adjacents:
            if not user in partial and self.adjacents[user] >= threshold:
                partial.add(user)
                new_adjacents.add(user)

        for user in new_adjacents:
            user.__getConnected__(threshold, partial)

        return partial

class UserGraph(object):
    def __init__(self):
        self.users = set()
        self.tokens = set()

    def addUserByNickname(self, nickname):
        newuser = User(self.generateToken(), nickname)
        self.users.add(newuser)
        return newuser

    def getUserByNickname(self, nickname):
        for user in self.users:
            if user.nickname == nickname:
                return user
        raise Exception("No user with nickname %s" % nickname)

    def getUserByToken(self, token):
        token = str(token)
        for user in self.users:
            if user.token == token:
                return user
        raise Exception("No user with token %s" % token)

    def generateToken(self):
        token = random.randint(0, 2**64-1)
        while(token in self.tokens):
            token = random.randint(0, 2**64-1)
        self.tokens.add(str(token))
        return str(token)

    def pushMessage(self, message):
        sending_user = self.getUserByToken(message.token)
        graph = sending_user.getConnected(0)
        if sending_user in graph:
            graph.remove(sending_user)
        totalSuccess = True
        for user in graph:
            if not user.getQueue().pushMessage(message):
                totalSuccess = False
        return totalSuccess

    def addConnections(self, user, nearby_users):
        user.addAdjacents(nearby_users)
        for otheruser in nearby_users:
            if otheruser == user:
                continue
            otheruser.addAdjacents([user])

    def updateConnections(self, user, nearby_users):
        user.updateAdjacents(nearby_users)
        for otheruser in nearby_users:
            if otheruser == user:
                continue
            otheruser.updateAdjacents([user])
