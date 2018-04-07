#!/usr/bin/env python

import socket, threading, sys, re, json, random

class ClientThread(threading.Thread):

    def __init__(self,ip, port, clientsocket, map, users, maplock, userlock):
        threading.Thread.__init__(self)
        self.maplock = maplock
        self.alias = ""
        self.userlock = userlock
        self.map = map
        self.users = users
        self.ip = ip
        self.port = port
        self.csocket = clientsocket
        self.state = "AUTHORIZATION"
        self.active = True
        self.commands = {'CONNECT': self.connect, 'QUIT': self.quit}
        print "[+] New thread started for "+ip+":"+str(port)

    def run(self):
        while self.active:
            data = self.csocket.recv(2048)
            print "Client(%s:%s) sent : %s"%(self.ip, str(self.port), data)
            self.csocket.send(self.interprete(data))

        print "Client at "+self.ip+" disconnected..."
    #tests
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
                    users[alias] = {"ip":self.ip,"port": self.port, "ressources":[]}
                    print (users)
                self.alias = alias
                self.state = "TRANSACTION"
                return "200 " + json.dumps(self.map)

            else:
                return "440 invalid username"
        else:
            return "480 Invalid Command"

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
        print ("blocking elments and ressources together cant be higher than 1.0")
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
        while True:
            try:
                tcpsock.listen(4)
                print "Listening for incoming connections on "+str(port)+"..."
                (clientsock, (ip, port)) = tcpsock.accept()
                print ("accepted client.")
                #pass clientsock to the ClientThread thread object being created
                newthread = ClientThread(ip, port, clientsock, map, users, maplock, userlock)
                newthread.start()
                threads.append(newthread)
            except KeyboardInterrupt:
                break
    finally:
        for t in threads:
            t.join()
        tcpsock.close()
        print ("closed server")