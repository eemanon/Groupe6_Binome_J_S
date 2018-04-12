#!/usr/bin/env python

import socket, threading, sys, re, json, random, ast, time, Queue, datetime

class LogThread(threading.Thread):
    """
    Logs connected users' commands into the file at the specified path.
    """
    def __init__(self, active, logQueue, path):
        threading.Thread.__init__(self)
        self.active = active
        self.logQueue = logQueue
        self.logpath = path

    def run(self):
        """
        Logs connected users' commands into the file at the specified path.
        :return: None
        """
        print("started Log Thread")
        with open(self.logpath + "spaceXlog.txt", "a") as f:
            print ("opened log file")
            while not self.active.is_set():
                if not self.logQueue.empty():
                    msg = self.logQueue.get(False)
                    f.write(msg)
        print("LogThread Closed")

class BroadCastThread(threading.Thread):
    """
    Broadcasts messages put into the broadCastQueue specified upon creation to all connected users
    Ideal for map updates
    """
    def __init__(self, users, userlock, active, broadCastQueue, map, maplock):
        threading.Thread.__init__(self)
        self.active = active
        self.broadCastQueue = broadCastQueue
        self.users = users
        self.userlock = userlock
        self.map = map
        self.maplock = maplock

    def run(self):
        print("started broadcast Thread")
        while not self.active.is_set():
            if not self.broadCastQueue.empty():
                msg = self.broadCastQueue.get(False)
                output = self.interprete(msg)
                print("sending to everyone the map...")
                with self.userlock:
                    for user, userprops in self.users.items():
                        userprops["mailbox"].put(output)
            time.sleep(0.01)
        print("Broadcast Thread Closed")

    def interprete(self, msg):
        if msg == "update":
            with self.maplock:
                return "100 " + json.dumps(self.map) + "\r\n"

class SendThread(threading.Thread):
    """
    A thread dedicated to sending responses to issued commands or spontaneous messages
    """
    def __init__(self, clientsocket, socketLock, queue, event):
        threading.Thread.__init__(self)
        self.socketLock = socketLock
        self.clientsocket = clientsocket
        self.active = event            #thread safe because atomic :)
        self.mailbox = queue

    def run(self):
        print("started Sender Thread")
        while not self.active.is_set():
            if not self.mailbox.empty():
                command = self.mailbox.get(False)
                print("send command received, sending "+command)
                with self.socketLock:
                    self.clientsocket.send(command.encode())
                    self.mailbox.task_done()
            time.sleep(0.01)
        print("SenderThread closed")

class SocketThread(threading.Thread):
    """
    Listens to client speciefied in clientsocket. Non blocking. Upon receival of a command, it is evaluated and put
    into the logQueue passed as argument. Then,
    the response is put into the its mailbox which is checked by the sender thread.
    Starts one sender thread per connection.
    The implemented commands are listed in the attribute "Commands"
    """
    def __init__(self,ip, port, clientsocket, map, users, maplock, userlock, broadCastQueue, activated, logQueue):
        threading.Thread.__init__(self)
        self.senderActive = threading.Event()
        self.maplock = maplock
        self.alias = ""
        self.userlock = userlock
        self.map = map
        self.users = users
        self.ip = ip
        self.paused = False
        self.mailbox = Queue.Queue()
        self.socketLock = threading.Lock()
        self.port = port
        self.sendThread = SendThread(clientsocket,self.socketLock, self.mailbox, self.senderActive)
        self.csocket = clientsocket
        self.state = "AUTHORIZATION"
        self.act = activated
        self.commands = {'CONNECT': self.connect, 'QUIT': self.quit, 'ADD': self.add,
                         'ASKTRANSFER': self.asktransfer, 'PAUSE': self.pause, 'RUN': self.unpause,
                         'NAME': self.newalias, 'UP': self.up, 'DOWN': self.down, 'LEFT':self.left,
                         'RIGHT': self.right, 'INFO': self.info, 'ACCEPTREQUEST': self.acceptrequest,
                         'REFUSEREQUEST': self.refuserequest}
        self.position = ()
        self.broadcastQueue = broadCastQueue
        self.logQueue = logQueue

    def run(self):
        print("Socket Thread started")
        self.logQueue.put(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +
                          "[" + self.ip + ", " + str(self.port) + "]: Connected")
        self.sendThread.start()
        while not self.act.is_set():
            with self.socketLock:
                try:
                    data = self.csocket.recv(2048)
                    self.logQueue.put(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +
                                      "["+self.ip+", "+str(self.port)+"]: "+data.decode())
                    self.mailbox.put(self.interprete(data))
                except:
                    pass
            time.sleep(0.1)
        self.senderActive.set()
        print("waiting for senderthread...")
        self.sendThread.join()
        self.csocket.close()
        print "SocketThread Closed"
        self.logQueue.put(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +
                          "[" + self.ip + ", " + str(self.port) + "]: Disconnected")

    # functions
    def connect(self, alias):
        """
        checks if username issued is valid and if so adds user to connected user's list,
        and responds with a copy of the map.
        :param alias: must be a valid alias consisting of digits and letters and length<30
        :return:
        """
        print ("connect command")
        if self.state == "AUTHORIZATION":
            print (alias)
            validUsername = re.search("^[a-zA-Z0-9]{1,31}$", alias)
            if validUsername:
                #check if username exists...
                with self.userlock:
                    if alias in users:
                        return "450 username Alias already in use. Please try another alias."
                #it doesnt so put it into the list with the information and confirm connection:
                    users[alias] = {"ip":self.ip,"port": self.port, "ressources":[], "requests":[],"mailbox":self.mailbox}
                    print (users)
                self.alias = alias
                self.state = "TRANSACTION"
                #create a thread with a queue and add the queue for all threads visible to the users
                return "200 " + json.dumps(self.map)

            else:
                return "440 invalid username"
        else:
            return "480 Invalid Command"

    def add(self, coords):
        """
        Adds a robot as specified in RFC 4.1
        :param coords: coordinates where to add the client's robot
        :return: None
        """
        if self.state == "TRANSACTION":
            pos = ()
            try:
                pos = ast.literal_eval(coords)
                #try placing robot on map...
                #check if blocking element on position
                with self.maplock:
                    #si la coordonate est libre cad pas dans la liste des blockingelements ni robots:
                    blocking = len(filter(lambda element: element["x"] == pos[0] and element["y"] == pos[1],self.map["blockingElements"]))
                    robots = len(filter(lambda element: element["x"] == pos[0] and element["y"] == pos[1], self.map["robots"]))
                    if (robots+blocking)==0:
                        print ("robot can be placed")
                        #placing robot...
                        #1 into map
                        self.map["robots"].append({"name":self.alias, "x":pos[0],"y":pos[1]})
                        #2 modifying its own coords
                        self.position = pos
                        print(self.map)
                        # issue map modified sequence for all threads
                        self.broadcastQueue.put("update")
                        return "210 robot is added"
                    else:
                        return "430 The coordinate is not free"


            except:
                return "400 Coordinates invalid"
        else:
            return "480 Please connect before adding a robot."

    def quit(self):
        """
        disconnects the client by setting the stop Event of the thread and its sender. Then checks if
        username set and removes it. Also removes the users robot, if there's any on the map.
        When the thread exits its loop, the socket is closed.
        :return:
        """
        print ("Disconnecting "+str(self.port))
        self.senderActive.set()
        self.act.set()
        if self.alias != "":
            with self.userlock:
                del users[self.alias]
            with self.maplock:
                del self.map["robots"][self.alias]
        return "240 Successfully disconnected"

    def asktransfer(self, username):
        """
        Checks if there's a user with the name provided and puts a request in the user's request list.
        Then puts a message in the target user's mailbox and informs the user that the request is submitted.
        :param username: target user's name to whom establish a connection
        """
        if self.state == "TRANSACTION":
            #check if user exists...
            with self.userlock:
                if username in users and username != self.alias:
                    #send this user a request to allow user 1 to have its infos
                    users[username]["mailbox"].put("110 Do you want to allow transfer from user "+self.alias+"\r\n")
                    #add request to users[username]["requests]
                    users[username]["requests"].append(self.alias)
                    return "280 request submitted, waiting for approval or refusal"
                else:
                    return "460 user not found"
        else:
            return "480 Please connect before trying to pause."

    def pause(self):
        """
        Pauses the robot as specified in RFC Section 4.3
        """
        if self.state == "TRANSACTION":
            with maplock:
                #check if its in maps...
                robot = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                print (robot)
                if len(robot) == 1:
                    self.paused = True
                    return "250 ("+ str(robot[0]["x"]) +","+ str(robot[0]["y"]) +")"
                else:
                    return "480 Please add a robot to the map before trying to pause."
        else:
            return "480 Please connect before trying to pause."

    def unpause(self):
        """
        unpauses the robot as specified in RFC Section 4.4
        """
        if self.state == "TRANSACTION":
            with maplock:
                #check if its in maps...
                robot = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                if len(robot) == 1:
                    self.paused = False
                    return "260"
                else:
                    return "480 Please add a robot to the map before trying to unpause."
        else:
            return "480 Please connect before trying to unpause."

    def newalias(self, alias):
        """
        replaces the current username by a new one if not yet taken by another user
        :param alias: the new user name
        """
        if self.state == "TRANSACTION":
            validUsername = re.search("^[a-zA-Z0-9]{1,31}$", alias)
            if validUsername:
                with self.userlock:
                    if alias in users:
                        return "450 username Alias already in use. Please try another alias."
                #it doesnt so exchange the current one
                    #1 in users
                    self.users[alias] = users[self.alias]
                    del users[self.alias]
                    #2 in map
                with self.maplock:
                    self.map["robots"] = [alias if x == self.alias else x for x in map["robots"]]
                print (users)
                self.alias = alias
                return "200 "+self.alias
            else:
                return "440 invalid username"
        else:
            return "480 Please connect before trying to change your username."

    def info(self):
        """
        Returns the ressources of the user and a list of all users connected.
        """
        if self.state == "TRANSACTION":
            #get ressources and users
            response = {"Ressources":[], "Users":[]}
            with self.userlock:
                    print (users[self.alias]["ressources"])
                    print (users.keys())
                    response["Ressources"] = users[self.alias]["ressources"]
                    response["Users"] = users.keys()
            return "200 "+json.dumps(response)
        else:
            return "480 Please connect before asking for user lists"

    def up(self):
        if not self.paused:
            if self.state == "TRANSACTION":
                with maplock:
                    #check if its in maps...
                    robots = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                    if len(robots) == 1:
                        #valid movement ( boundaries, obstacles?)
                        if self.validCoords((robots[0]["x"], robots[0]["y"]+1)):
                            robots[0]["y"]=robots[0]["y"]+1
                            # ressources found?
                            self.harvestRessources((robots[0]["x"], robots[0]["y"]))
                        else:
                            return "430 Invalid Coordinates"
                    else:
                        return "480 Please add a robot to the map before trying to move it."
                print self.map
                #update map message
                self.broadcastQueue.put("update")
                return "270 ("+ str(robots[0]["x"]) +","+ str(robots[0]["y"]) +")"
            else:
                return "480 Please connect before trying to move a robot."
        else:
            return "430 Robot paused"
    def down(self):
        if not self.paused:
                if self.state == "TRANSACTION":
                    with maplock:
                        # check if its in maps...
                        robots = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                        if len(robots) == 1:
                            # valid movement ( boundaries, obstacles?)
                            if self.validCoords((robots[0]["x"], robots[0]["y"] - 1)):
                                robots[0]["y"] = robots[0]["y"] - 1
                                # ressources found?
                                self.harvestRessources((robots[0]["x"], robots[0]["y"]))
                            else:
                                return "430 Invalid Coordinates"
                        else:
                            return "480 Please add a robot to the map before trying to move it."
                    print self.map
                    # update map message
                    self.broadcastQueue.put("update")
                    return "270 (" + str(robots[0]["x"]) + "," + str(robots[0]["y"]) + ")"
                else:
                    return "480 Please connect before trying to move a robot."
        else:
            return "430 Robot paused"

    def right(self):
        if not self.paused:
            if self.state == "TRANSACTION":
                with maplock:
                    #check if its in maps...
                    robots = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                    if len(robots) == 1:
                        #valid movement ( boundaries, obstacles?)
                        if self.validCoords((robots[0]["x"]+1, robots[0]["y"])):
                            robots[0]["x"]=robots[0]["x"]+1
                            # ressources found?
                            self.harvestRessources((robots[0]["x"], robots[0]["y"]))
                        else:
                            return "430 Invalid Coordinates"
                    else:
                        return "480 Please add a robot to the map before trying to move it."
                print self.map
                #update map message
                self.broadcastQueue.put("update")
                return "270 ("+ str(robots[0]["x"]) +","+ str(robots[0]["y"]) +")"
            else:
                return "480 Please connect before trying to move a robot."
        else:
            return "430 Robot paused"

    def left(self):
        if not self.paused:
            if self.state == "TRANSACTION":
                with maplock:
                    #check if its in maps...
                    robots = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                    if len(robots) == 1:
                        #valid movement ( boundaries, obstacles?)
                        if self.validCoords((robots[0]["x"], robots[0]["y"]+1)):
                            robots[0]["x"]=robots[0]["x"]-1
                            # ressources found?
                            self.harvestRessources((robots[0]["x"], robots[0]["y"]))
                        else:
                            return "430 Invalid Coordinates"
                    else:
                        return "480 Please add a robot to the map before trying to move it."
                print self.map
                #update map message
                self.broadcastQueue.put("update")
                return "270 ("+ str(robots[0]["x"]) +","+ str(robots[0]["y"]) +")"
            else:
                return "480 Please connect before trying to move a robot."
        else:
            return "430 Robot paused"

    def interprete(self, cmd):
        """
        This function evaluates a raw string send from a client. If the command
        is a known, valid function, the corresponding function is picked and evaluated.
        :param cmd: the string submitted
        :return: the server's response to the string submitted
        """

        cmd_list = cmd.split()
        #print ("interpreting command "+str(cmd_list[0]))
        #try:
        if cmd_list[0] in self.commands and len(cmd_list)==2:
            print ("length =2")
            return self.commands[cmd_list[0]](cmd_list[1])+"\r\n"
        elif cmd_list[0] in self.commands and len(cmd_list)==3:
            print ("length =3")
            return self.commands[cmd_list[0]](cmd_list[1],cmd_list[2])+"\r\n"
        elif cmd_list[0] in self.commands and len(cmd_list)==4:
            print ("length =4")
            return self.commands[cmd_list[0]](cmd_list[1],cmd_list[2], cmd_list[3])+"\r\n"
        elif cmd_list[0] in self.commands and len(cmd_list)==1:
            print("length = 1")
            return self.commands[cmd_list[0]]()+"\r\n"
        else:
            return "480 Inexisting Command\r\n"
        #except:
            #return "480 Malformed Command\r\n"

    def acceptrequest(self, user, port, protocol):
        """
        A subcommand of asktransfer with which the transfer request can be answered positively
        :param user: the user having requested the transfer previously
        :param port: the port which the sender will open for the transfer
        :param protocol: the protocol for the transfer
        """
        #check if there is a request from this user in the user's request list...
        with self.userlock:
            if user in users[self.alias]["requests"]:
            # if so, send data of user to requesting user's mailbox
                users[user]["mailbox"].put("230 "+users[user]["ip"]+" "+port+" "+protocol+"\r\n")
            #remove request from users requet list
                del users[self.alias]["requests"][user]
                return "200 answer submitted"
            else:
                # else send no user found
                return "460 user not found in your requestlist."
    
    def refuserequest(self, user):
        """
        negative answer of a user to the asktransfer command issued by another user.
        :param user: the user having issued the request
        :return:
        """
        with self.userlock:
            if user in users[self.alias]["requests"]:
            # if so, send refusal message
                users[user]["mailbox"].put("470 Connection refused by "+user+"\r\n")
                del users[self.alias]["requests"][user]
                return "200 answer submitted"
            else:
                # else send no user found
                return "460 user not found in your requestlist."

    def harvestRessources(self, coords):
        """
        ONLY TO BE CALLED WITH MAPLOCK ACQUIRED!
        :coords param: coordinates where ressources are harvested
        :return: void
        """
        for element in self.map["ressources"]:
            if element["x"]==coords[0] and element["y"]==coords[1]:
                #there is a ressource on the spot! adding it to the users basket
                print ("ressource found! harvesting...")
                with userlock:
                    print (self.users)
                    self.users[self.alias]["ressources"].append(element["name"])
                #remove it from map
                del element

    def validCoords(self, coords):
        """
        ONLY TO BE CALLED WITH MAPLOCK ACQUIRED!
        :param coords: checks these coordinates for blocking elements
        :return: true if coordinate is not blocking, false otherwise
        """
        #out of boundaries?
        if(coords[0]>=self.map["dimensions"][0] or coords[0]<0 or
                   coords[1]>=self.map["dimensions"][1] or coords[1]<0):
            return False
        #obstacle?
        for element in self.map["blockingElements"]:
            if element["x"]==coords[0] and element["y"]==coords[1]:
                return False
        return True

def createMap(size, blockingElements, ressources):
    """
    :param size: size of map
    blockingElements: percentage as float between 0 and 1 of blocking elements covering the map
    ressources: percentage as float between 0 and 1 of ressources covering the map.
    blockingElements + ressources must be < 1
    :return: a dictionnary with dimensions, blocking elements, ressources and robots.
    the latter is an initially empty array.
    """
    if blockingElements+ressources>1.0:
        print ("blocking elements and ressources together cant be higher than 1.0")
        exit(1)
    blocktypes = ["rock", "plant", "hole"]
    ressourcetypes = ["Gold", "Diamant"]
    map = {"dimensions": [size, size], "blockingElements":[], "ressources": [], "robots":[]}
    #Create blocking elements on map....
    #make a list of distinct coords
    print ("Populating map with " +str(round(size*size*blockingElements))+ " blocking Elements...")
    coords = set()
    while len(coords) < int(round(size*size*blockingElements)):
        coords.add((random.randint(0, size), random.randint(0, size)))
    for coordinate in coords:
        map["blockingElements"].append({"name": blocktypes[random.randint(0,len(blocktypes)-1)], "x":coordinate[0], "y":coordinate[1]})
    #Create Ressources for map...
    # make a list of distinct coords: copy coords, make it until size + size*ressources and the diff coords
    ress_coords = coords.copy()
    print ("Populating map with " + str(round(size*size*ressources)) + " ressources...")
    while len(ress_coords) < int(round(size*size*blockingElements)+round(size*size*ressources)):
        ress_coords.add((random.randint(0, size), random.randint(0, size)))
    ress_coords = ress_coords.difference(coords)
    for coordinate in ress_coords:
        map["ressources"].append({"name": ressourcetypes[random.randint(0,len(ressourcetypes)-1)], "x":coordinate[0], "y":coordinate[1]})
    print ("Map Creation Finished")
    return map

def loadConfig():
    """
    loads a config file. Must be of this structure:
    <property1> <value1>
    <property2> <value2>
    :return: a dictionnary of the file's content.
    The following keys are set by default: port, path
    """
    config = {"port": 9021, "path":""}
    with open("spaceX.conf", "r") as r:
        for line in r:
            conf = line.split()
            config[conf[0]] = conf[1]
    if (len(sys.argv) >= 2):
        config["port"] = sys.argv[1]
    return config

if __name__ == '__main__':

    #1 Load Configuration
    config = loadConfig()
    #2 Define Global Ressources
    users = {}
    map = createMap(10, 0.1, 0.2)
    maplock = threading.Lock()
    userlock = threading.Lock()

    #3 Define broadcasting mechanism for messages to all connected clients
    broadcastMailbox = Queue.Queue()
    broadcastActive = threading.Event()
    broadcastthread = BroadCastThread(users, userlock, broadcastActive, broadcastMailbox, map, maplock)

    #4 Define Logging mechanism to keep track of clients' commands.
    logQueue = Queue.Queue()
    logActive = threading.Event()
    logthread = LogThread(logActive,logQueue,config["path"])
    logthread.start()

    host ='localhost'

    logQueue.put("\n"+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +
                 " server started @ "+host+" port "+str(config["port"]))

    threads = []
    events = []
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    tcpsock.bind((host,int(config["port"])))
    try:
        broadcastthread.start()
        print ("Listening for incoming connections on " + str(config["port"]) + "...")

        while True:
            try:
                tcpsock.listen(4)
                #pass clientsock to the ClientThread thread object being created
                (clientsock, (ip, port)) = tcpsock.accept()
                print ("accepted client.")
                clientsock.settimeout(60)
                clientsock.setblocking(0)
                ev = threading.Event()
                newthread = SocketThread(ip, port, clientsock, map, users, maplock,
                                         userlock, broadcastMailbox, ev, logQueue)
                print ("starting thread...")
                newthread.start()
                print ("thread started...")
                threads.append(newthread)
                events.append(ev)
            except KeyboardInterrupt:
                break
    finally:

        for ev in events:
            ev.set()
        for t in threads:
            t.join()

        logQueue.put("\n" + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +
                     " server halted @ " + host + " port " + str(config["port"]))

        print("terminating broadcast thread...")
        broadcastActive.set()
        broadcastthread.join()
        print("terminating log thread...")
        logActive.set()
        logthread.join()
        tcpsock.close()
        print ("closed server")