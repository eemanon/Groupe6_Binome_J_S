from socket import *
import sys, threading
from datetime import datetime
import time
import utilisateur, map , requetes


def loadConfig():
    with open("spaceX.conf", "r") as r:
        config = {}
        for line in r:
            conf = line.split(" ")
            config[conf[0]] = conf[1].rstrip()
    if (len(sys.argv) >= 2):
        config["port"] = sys.argv[1]
    return config


def traiter_client(client, adr):
    statut = "DISCONNECT"
    nom_client = ""
    clients_connect.append((client, adr, nom_client))
    while True:
        pr_term = (dateInit.strftime("%d/%m/%Y %H:%M:%S") + "> En attente d'une requête du client " + str(adr))
        # Récupération de la requête du client
        req = client.recv(TAILLE_TAMPON)
        pr_term = (dateInit.strftime("%d/%m/%Y %H:%M:%S")+ "> Réception du client " + str(adr))
        # Décodage du message en string
        mess = req.decode().upper()
        if len(mess) == 0:
            if mess.upper() == "QUIT":
                reponse = (code_success("240") + "\nDéconnexion du client")
                client.send(reponse_serveur(reponse).encode())
            break
        # Construction de la réponse encodée
        (reponse, statut, nom_client) = retour_requete(mess, statut, nom_client)
        for s, a, p in clients_connect:
            if adr == a and nom_client != p:
                (s, a, p) = (s, a, nom_client)
                print((s, a, p))
        # Envoi de la réponse au client
        pr_term = (dateInit.strftime("%d/%m/%Y %H:%M:%S") + "> Envoie de la réponse : " + reponse  + "\n")
        client.send(reponse.encode())
        with open("serveurLog.txt", "a") as f:
            f.write(pr_term)
    print("requête traité")
    client.close()


def retour_requete(mess,statut, pseudo):
    args = mess.split(" ")
    modCarte = False
    if args[0] == "CONNECT":
        (reponse, statut, pseudo) = requetes.connect(args,ip_client)
    elif args[0] == "ADD":
        (reponse, statut) = requetes.add(args,ip_client)
        modCarte = True
    elif args[0] == "NAME":
        (reponse, pseudo) = requetes.name(args, ip_client)
        modCarte = True
    elif args[0] == "INFO":
        reponse = requetes.info(ip_client)
    elif args[0] == "UP":
        reponse = requetes.up(ip_client)
        modCarte = True
    elif args[0] == "DOWN":
        reponse = requetes.down(ip_client)
        modCarte = True
    elif args[0] == "LEFT":
        reponse = requetes.left(ip_client)
        modCarte = True
    elif args[0] == "RIGHT":
        reponse = requetes.right(ip_client)
        modCarte = True

    elif args[0] == "ASKTRANSFER":
        reponse = requetes.asktransfer(args,ip_client)
    elif args[0] == "PAUSE":
        (reponse, statut) = requetes.pause(ip_client)
    elif args[0] == "RUN":
        (reponse, statut) = requetes.run(ip_client)
    elif args[0] == "UPDATE":
        reponse = requetes.updateMap()
    else:
        reponse = f"480 Invalid Command"
    if modCarte:
        client_refresh_map()

    return (reponse, statut, pseudo)

# Transfert de la map à tous les clients
def client_refresh_map():
    for c in list_clients:
        try:
            c.send(requetes.updateMap().encode())
        except:
            c.close()



# Liste des sockets clients connectées
list_clients = []

# Liste des pseudos et adresse client
clients_connect = []

# Liste des threads
list_threads = []

#Configuration
config = loadConfig()
TAILLE_TAMPON = 256
sock_serveur  = socket(AF_INET, SOCK_STREAM)
# Liaison de la socket à toutes les IP possibles de la machine
sock_serveur.bind(("", int(config["port"])))
print("Serveur en attente sur le port " + config["port"], file=sys.stderr)
dateInit = datetime.now()
with open("serveurLog.txt", "a") as f:
    f.write(dateInit.strftime("%d/%m/%Y %H:%M:%S") + " Server started\n")
    f.write(dateInit.strftime("%d/%m/%Y %H:%M:%S") + " Listen on: " + str(config["port"]) + "\n")
sock_serveur.listen(5)
#Server is listening
while True:
    try:
        # Récupération de la requête du client
        requete = sock_serveur.accept()
        # Extraction du message et de l’adresse sur le client
        (sock_client, adr_client) = requete
        ip_client, port_client = adr_client
        list_clients.append(sock_client)
        list_threads.append(((threading.Thread(target=traiter_client, args=(sock_client, adr_client)) \
            .start()), adr_client))
    except KeyboardInterrupt:
        break

sock_serveur.shutdown(SHUT_RDWR)

for c in list_clients:
    c.close()

for t in threading.enumerate():
    if t != threading.main_thread():
        t.join()

print("Arrêt du serveur", file=sys.stderr)
with open(config["path"] + "serveurLog.txt", "a") as f:
    date = datetime.now()
    f.write(date.strftime("%d/%m/%Y %H:%M:%S") + " Server stopped...\n\n")
#Serialization map
map.serializationMap()
map.serializationRessources()
sys.exit(0)
