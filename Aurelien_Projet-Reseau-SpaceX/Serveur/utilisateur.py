import map


users = {}


def addUser(pseudo,ip):
    users[pseudo] = ip


def delUser(pseudo):
    users.pop(pseudo)


def listOfConnectedUsers():
    list = []
    for userName in users.keys():
        list.append(userName)
    return list


def userIsConnected(ip):
    for user in users.keys():
        if users[user] == ip:
            return True
    return False


def getUserByIP(ip):
    for user in users.keys():
        if users[user] == ip:
            return user


def changeName(newName, robot):
    users[newName] = users.pop(robot["name"])
    robot["name"] = newName
