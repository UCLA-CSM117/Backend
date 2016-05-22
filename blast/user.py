import random

class User(object):
    def __init__(self, token, nickname):
        self.nickname
        self.adjacents = []

    def getQueue(self):
        # TODO: Implement
        pass

class UserGraph(object):
    def __init__(self):
        self.users = []
        self.tokens = []

    def addUserByNickname(self, nickname):
        newuser = User(generateToken(), nickname)
        users.append(newuser)
        return newuser

    def getUserByNickname(self, nickname):
        for user in self.users:
            if user.nickname == nickname:
                return user
        return None

    def getUserByToken(self, token):
        # TODO: Implement
        pass

    def generateToken(self):
        token = random.randint(0, 2**64-1)
        while(token in self.tokens):
            token = random.randint(0, 2**64-1)
        self.tokens.append(token)
        return token
        

