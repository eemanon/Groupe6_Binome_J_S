#!/usr/bin/env python

import socket, threading, sys, re, json, random, ast, time, Queue


class BroadCastThread(threading.Thread):
    def __init__(self, users, userlock, active, broadCastQueue, map, maplock):
        threading.Thread.__init__(self)
        self.active = active
        self.broadCastQueue = broadCastQueue
        self.users = users
        self.userlock = userlock
        self.map = map
        self.maplock = maplock

    def run(self):
        while self.active:
            msg = self.broadCastQueue.get()
            output = self.interprete(msg)
            print("sending to everyone the map...")
            with self.userlock:
                for user, userprops in self.users.items():
                    userprops["mailbox"].put(output)
    def interprete(self, msg):
        if msg == "update":
            with self.maplock:
                return "100 " + json.dumps(self.map)+"\r\n"

class SendThread(threading.Thread):

    def __init__(self, clientsocket, socketLock, active, queue):
        threading.Thread.__init__(self)
        self.socketLock = socketLock
        self.clientsocket = clientsocket
        self.active = active            #thread safe because atomic :)
        self.mailbox = queue

    def run(self):
        while self.active:
            command = self.mailbox.get()
            print("send command received, sending "+command)
            with self.socketLock:
                self.clientsocket.send(command)
                self.mailbox.task_done()
            time.sleep(0.01)

class ClientThread(threading.Thread):
    def __init__(self,ip, port, clientsocket, map, users, maplock, userlock, broadCastQueue):
        threading.Thread.__init__(self)
        self.senderActive = True
        self.maplock = maplock
        self.alias = ""
        self.userlock = userlock
        self.map = map
        self.users = users
        self.ip = ip
        self.mailbox = Queue.Queue()
        self.socketLock = threading.Lock()
        self.port = port
        self.sendThread = SendThread(clientsocket,self.socketLock, self.senderActive, self.mailbox)
        self.csocket = clientsocket
        self.state = "AUTHORIZATION"
        self.active = True
        self.commands = {'CONNECT': self.connect, 'QUIT': self.quit, 'ADD': self.add,
                         'ASKTRANSFER': self.asktransfer, 'PAUSE': self.pause, 'RUN': self.run,
                         'NAME': self.name, 'UP': self.up, 'DOWN': self.down, 'LEFT':self.left,
                         'RIGHT': self.right}
        self.position = ()
        self.broadcastQueue = broadCastQueue
        print "[+] New thread started for "+ip+":"+str(port)

    def run(self):
        self.sendThread.start()
        while self.active:
            with self.socketLock:
                data = self.csocket.recv(2048)
                print "Client(%s:%s) sent : %s"%(self.ip, str(self.port), data)
                self.mailbox.put(self.interprete(data))
            time.sleep(0.01)

        print "Client at "+self.ip+" disconnected..."

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
                    users[alias] = {"ip":self.ip,"port": self.port, "ressources":[], "mailbox":self.mailbox}
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
        print ("Disconnecting "+str(self.port))
        self.active = False
        if self.alias != "":
            with self.userlock:
                del users[self.alias]
        self.csocket.close()
        return "240 Successfully disconnected"

    def interprete(self, cmd):
        """
        This function evaluates a raw string send from a client. If the command
        is a known, valid function, the corresponding function is picked and evaluated.
        :param cmd: the string submitted
        :return: the server's response to the string submitted
        """
        print ("interpreting command..")
        cmd_list = cmd.split()
        if cmd_list[0] in self.commands and len(cmd_list)>1:
            return self.commands[cmd_list[0]](cmd_list[1])+"\r\n"
        elif cmd_list[0] in self.commands and len(cmd_list)==1:
            return self.commands[cmd_list[0]]()+"\r\n"
        else:
            return "480 Invalid Command\r\n"

    def asktransfer(self, username):
        return "400 Not implemented yet"

    def pause(self):
        return "400 Not implemented yet"

    def run(self):
        return "400 Not implemented yet"

    def name(self, name):
        return "400 Not implemented yet"

    def info(self):
        return "400 Not implemented yet"

    def up(self):
        return "400 Not implemented yet"

    def down(self):
        return "400 Not implemented yet"

    def right(self):
        return "400 Not implemented yet"

    def left(self):
        return "400 Not implemented yet"

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

if __name__ == '__main__':
    #deux ressources globales: Carte et Liste d'utilisateurs
    users = {}
    map = createMap(10, 0.1, 0.2)
    maplock = threading.Lock()
    userlock = threading.Lock()
    broadcasting = True
    broadcastMailbox = Queue.Queue()
    broadcastthread = BroadCastThread(users, userlock, broadcasting, broadcastMailbox, map, maplock)

    if (len(sys.argv) < 2):
        print("specify a port s'il vous plait")
        exit()
    threads = []
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host ='localhost'
    port = int(sys.argv[1])
    tcpsock.bind((host,port))
    try:
        broadcastthread.start()
        while True:
            try:
                tcpsock.listen(4)
                print "Listening for incoming connections on "+str(port)+"..."
                (clientsock, (ip, port)) = tcpsock.accept()
                print ("accepted client.")
                #pass clientsock to the ClientThread thread object being created
                newthread = ClientThread(ip, port, clientsock, map, users, maplock, userlock, broadcastMailbox)
                newthread.start()
                threads.append(newthread)
            except KeyboardInterrupt:
                break
    finally:
        for t in threads:
            t.join()
        tcpsock.close()
        print ("closed server")