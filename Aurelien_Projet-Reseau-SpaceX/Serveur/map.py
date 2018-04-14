import json
import utilisateur

def serializationMap():
    with open("map.json","w") as f:
        str = json.dumps(map)
        f.write(str)


def deserializationMap():
    with open("map.json","r") as f:
        data = json.loads(f.read())
    return data


def deserializationRessources():
    with open("ressources.json","r") as f:
        data = json.loads(f.read())
    return data


def serializationRessources():
    with open("ressources.json","w") as f:
        str = json.dumps(collectedRessources)
        f.write(str)


def getMapJSON():
    return json.dumps(map)


def getRobotByName(username):
    for robot in map["robots"]:
        if robot["name"] == username:
            return robot
    return None


def getListRessources(user):
    if user in collectedRessources.keys():
        list = collectedRessources[user]
    else:
        list = []
    return list


def getRobotByIP(ip):
    actualName = utilisateur.getUserByIP(ip)
    for robot in map["robots"]:
        if robot["name"] == actualName:
            return robot
    return None


def addRobotToRessourcesList(robotName):
    collectedRessources[robotName] = []


def delRobotFromRessourcesList(robotName):
    collectedRessources.remove(robotName)


def addRessourceToRobotRessourcesList(robotName,ressourceAajouter):
    collectedRessources[robotName].append(ressourceAajouter)


def delRessourceFromMap(ressource):
    return map["ressources"].pop(ressource)


def changeUserNameRess(newname,robot):
    print(robot)
    collectedRessources[newname] = collectedRessources.pop(robot["name"])


def addPosition(pseudo,posStr,cate):
    posStr = posStr.replace("(","")
    posStr = posStr.replace(")","")
    pos = posStr.split(",")
    element={"name": pseudo,
            "x": int(pos[0]),
            "y": int(pos[1])}
    if isPosAlreadyUsed(element["x"],element["y"]):
        return "430 the coordinate is not free"
    else:
        map[cate].append(element)
        return f"210 {cate} is added"


def isPosAlreadyUsed(x,y):
    for categories in map.keys():
        if categories != "dimensions":
            for elem in map[categories]:
                if elem["x"] == x and elem["y"] == y:
                    return True
    return False

def isPosAccesible(x,y,username):
    if x < 0 or x > map["dimensions"][0] or y < 0 or y >  map["dimensions"][1]:
        return False
    for categories in map.keys():
        if categories != "dimensions" and categories != "ressources":
            for elem in map[categories]:
                if elem["x"] == x and elem["y"] == y:
                    return False
        if categories == "ressources":
            for ressource in map[categories]:
                if ressource["x"] == x and ressource["y"] == y:
                    ressName = ressource['name']
                    addRessourceToRobotRessourcesList(username, ressName)
                    delRessourceFromMap(ressource)
    return True

map = deserializationMap()
collectedRessources = deserializationRessources()
print (collectedRessources)
