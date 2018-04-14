import utilisateur
import map

paused_robots = []


def addRobotToPausedList(robotName):
    paused_robots.append(robotName)


def delRobotFromPausedList(robotName):
    paused_robots.remove(robotName)



def moveUp(ip):
    username = utilisateur.getUserByIP(ip)
    robot = map.getRobotByName(username)
    if username in paused_robots:
        return "can't move - unpause"
    if robot == None:
        return "??? pas de robot"
    if map.isPosAccesible(robot["x"],robot["y"]+1,username):
        robot["y"] = robot["y"]+1
        return f"270 ({robot['x']},{robot['y']})"
    return f"400 can't move here ({robot['x']},{robot['y']})"

def moveDown(ip):
    username = utilisateur.getUserByIP(ip)
    robot = map.getRobotByName(username)
    if username in paused_robots:
        return "can't move - unpause"
    if robot == None:
        return "??? pas de robot"
    if map.isPosAccesible(robot["x"],robot["y"]-1,username):
        robot["y"] = robot["y"]-1
        return f"270 ({robot['x']},{robot['y']})"
    return f"400 can't move here ({robot['x']},{robot['y']})"

def moveLeft(ip):
    username = utilisateur.getUserByIP(ip)
    robot = map.getRobotByName(username)
    if username in paused_robots:
        return "can't move - unpause"
    if robot == None:
        return "??? pas de robot"
    if map.isPosAccesible(robot["x"]-1,robot["y"],username):
        robot["x"] = robot["x"]-1
        return f"270 ({robot['x']},{robot['y']})"
    return f"400 can't move here ({robot['x']},{robot['y']})"

def moveRight(ip):
    username = utilisateur.getUserByIP(ip)
    robot = map.getRobotByName(username)
    if username in paused_robots:
        return "can't move - unpause"
    if robot == None:
        return "??? pas de robot"
    if map.isPosAccesible(robot["x"]+1,robot["y"],username):
        robot["x"] = robot["x"]+1
        return f"270 ({robot['x']},{robot['y']})"
    return f"400 can't move here ({robot['x']},{robot['y']})"
