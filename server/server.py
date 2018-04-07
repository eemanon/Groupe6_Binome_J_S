import socket
import sys
import time
import datetime
import re


state = "connect"

#functions
def connect(alias):
    print ("connect command")
    validUsername = re.search("^[a-zA-Z0-9]+${1,31}", alias)
    if validUsername:
        global state
        state = "transaction"
        return "200 hello, "+alias

    else:
        return "440 invalid username"



def interprete(cmd):
    cmd_list = cmd.split()
    if cmd_list[0] in commands:
        return commands[cmd_list[0]](cmd_list[1])
    else:
        return "480 Invalid Command"

commands = {'CONNECT':connect}

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("specify a port s'il vous plait")
        exit()

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the address given on the command line
    port = int(sys.argv[1])
    server_address = ("localhost", port)
    print >> sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    sock.listen(1)
    #Logging
    f = open('serveurDate.log', 'a')
    try:
        f.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " Server started\n")
        f.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " Listening on " + str(port) + "\n")

        while True:
            print >> sys.stderr, 'waiting for a connection'
            connection, client_address = sock.accept()
            try:
                print >> sys.stderr, 'client connected:', client_address
                while True:
                    data = connection.recv(16)
                    print >> sys.stderr, 'received "%s"' % data
                    if data:
                        f.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " " + str(data.decode()) + "\n")
                        reponse = interprete(data.decode().upper())
                        print (reponse)
                        connection.sendall(reponse.encode())
                    else:
                        break
            except KeyboardInterrupt:
                break
    finally:
        connection.close()
        f.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " Server stopped\n")
        f.close()