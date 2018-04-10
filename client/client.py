from socket import *
import sys
import json
import threading
import time

#ip = localhost
#port = 9021

""""if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <ip> <port>", file=sys.stderr)
    sys.exit(1)

SERVER = sys.argv[1]
PORT = int(sys.argv[2])
TAILLE_TAMPON = 256
"""

SERVER = "localhost"
PORT = 8001
TAILLE_TAMPON = 10240

class ListenThread(threading.Thread):
    
    def __init__(self, sock, lock, event):
        threading.Thread.__init__(self)
        self.lock = lock
        self.sock = sock
        self.event = event
        
    def run(self):
        while not self.event.is_set():
            self.lock.acquire()
            try:
                reponse = sock.recv(TAILLE_TAMPON)
            finally:
                self.lock.release()
            print("Reponse = " + reponse.decode())
        

with socket(AF_INET, SOCK_STREAM) as sock:
    sock.connect((SERVER, PORT))
    event_stop = threading.Event()
    lock_thread = threading.Lock()
    
    rep = ListenThread(sock, lock_thread, event_stop)
    rep.start()
    
    print(f"Connexion vers {SERVER} : {str(PORT)} reussie.")

    while True:

        msg = input("Entrez une commande : ")       

        # Envoi de la requête au serveur après encodage de str en bytes
        lock_thread.acquire() 
        
        if msg == "quit" :
            sock.send(msg.upper().encode())
            event_stop.set()
            rep.join()
            break
            
        
        print("with main")
        sock.send(msg.upper().encode())
        lock_thread.release()

        # Réception de la réponse du serveur et décodage de bytes en str
        #reponse = sock.recv(TAILLE_TAMPON)
        #print("Réponse = " + reponse.decode())
    
    print ("Deconnexion.")
    sock.close()

