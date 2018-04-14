import utilisateur, map, robot
import json

def connect(requete,ip_client):

    if requete[1] and len(requete) == 2:
        if requete[1] in utilisateur.users:
            reponse = "450 username Alias already in use. Please try another alias."
            statut = "DISCONNECT"
            pseudo = requete[1]
        else:
            utilisateur.addUser(requete[1],ip_client)
            reponse = "220 " + map.getMapJSON()
            statut = "CONNECT"
            pseudo = requete[1]
    else:
        reponse = "440 username invalid"
        statut = "DISCONNECT"
        pseudo = requete[1]
    return reponse,statut,pseudo


def add(requete,ip_client):
    if utilisateur.userIsConnected(ip_client):
        pseudo = utilisateur.getUserByIP(ip_client)
        onMap = False
        for robot in map.map["robots"]:
            if robot["name"] == pseudo:
                reponse = "430 Robot is already on the map"
                onMap = True
        if not onMap:
            map.addRobotToRessourcesList(pseudo)
            reponse = map.addPosition(pseudo,requete[1],"robots")
        statut = "EXPLORE"
    else:
        reponse = "430 User is not connected"
        statut = "DISCONNECT"

    return reponse, statut


def asktransfer(requete,ip_client):
    # TO DO
    reponse = "480 Invalid Command"
    return reponse


def pause(ip_client):
    username = utilisateur.getUserByIP(ip_client)
    LPausedRobots = robot.paused_robots
    print(LPausedRobots)
    if username not in LPausedRobots:
        robot.addRobotToPausedList(username)
        reponse = "250 Paused"

    else:
        reponse = "444 Already Paused"
    statut = "PAUSE"
    return reponse, statut


def run(ip_client):
    username = utilisateur.getUserByIP(ip_client)
    LPausedRobots = robot.paused_robots
    print(LPausedRobots)
    if username in LPausedRobots:
        robot.delRobotFromPausedList(username)
        reponse = "260"
    else:
        reponse = "445 Robot is not in pause"
    statut = "EXPLORE"
    return reponse, statut


def name(requete, ip_client):
    actualName = utilisateur.getUserByIP(ip_client)
    robotAModif = map.getRobotByIP(ip_client)
    if requete[1] and len(requete) == 2:
        if requete[1] in utilisateur.users:
            reponse = "450 username Alias already in use. Please try another alias."
        else:
            map.changeUserNameRess(requete[1], robotAModif)
            utilisateur.changeName(requete[1], robotAModif)
            reponse = f"200 {requete[1]}"
    else:
        reponse = "440 username invalid"
    return reponse, requete[1]


def info(ip_client):
    reponse = {}
    user = utilisateur.getUserByIP(ip_client)
    listOfUsersOnline = utilisateur.listOfConnectedUsers()
    listOfRessources = map.getListRessources(user)
    reponse["Ressources"] = listOfRessources
    reponse["Users"] = listOfUsersOnline
    return "200 " + json.dumps(reponse)


def up(ip_client):
    reponse = robot.moveUp(ip_client)
    return reponse


def down(ip_client):
    reponse = robot.moveDown(ip_client)
    return reponse


def left(ip_client):
    reponse = robot.moveLeft(ip_client)
    return reponse


def right(ip_client):
    reponse = robot.moveRight(ip_client)
    return reponse

def updateMap():
    return "100 " + map.getMapJSON()


def quit(ip_client):
    user = utilisateur.getUserByIP(ip_client)
    if user is not None:
        utilisateur.delUser(user)
    return "240 Successfully disconnected"
