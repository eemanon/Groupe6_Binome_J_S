from socket import *
import sys
from datetime import datetime
import time
import utilisateur, map , requetes


def loadConfig():
    with open("spaceXserver.conf", "r") as r:
        config = {}
        for line in r:
            conf = line.split(" ")
            config[conf[0]] = conf[1].rstrip()
    if (len(sys.argv) >= 2):
        config["port"] = sys.argv[1]
    return config

config = loadConfig()
TAILLE_TAMPON = 256
sock = socket(AF_INET, SOCK_DGRAM)
#Load map

# Liaison de la socket à toutes les IP possibles de la machine
sock.bind(("", int(config["port"])))
print("Serveur en attente sur le port " + config["port"], file=sys.stderr)
dateInit = datetime.now()
with open("serveurLog.txt", "a") as f:
    f.write(dateInit.strftime("%d/%m/%Y %H:%M:%S") + " Server started\n")
    f.write(dateInit.strftime("%d/%m/%Y %H:%M:%S") + " Listen on: " + str(config["port"]) + "\n")

#Server is listening
while True:
    try:
        # Récupération de la requête du client
        msg = sock.recvfrom(TAILLE_TAMPON)
        # Extraction du message et de l’adresse sur le client
        (mess, adr_client) = msg
        ip_client, port_client = adr_client
        print(f"Requête provenant de {ip_client}. Longueur = {len(mess)}",
                    file=sys.stderr)
        # Construction de la réponse
        request = mess.decode().upper()
        #On écrit la requête reçue
        with open("serveurLog.txt","a") as f:
            date = datetime.now()
            f.write(date.strftime("%d/%m/%Y %H:%M:%S") + f"Received {request} from {adr_client[0]}:{adr_client[1]}\n")


        # Envoi de la réponse au client
        args = request.split(" ")
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
        elif args[0] == "QUIT":
            reponse = requetes.quit(ip_client)
            sock.sendto(reponse.encode(), adr_client)
            break
        elif args[0] == "UPDATE":
            reponse = requetes.updateMap()
        else:
            reponse = f"480 Invalid Command"
        sock.sendto(reponse.encode(), adr_client)
    except KeyboardInterrupt:
        break

sock.close()
print("Arrêt du serveur", file=sys.stderr)
with open(config["path"] + "serveurLog.txt", "a") as f:
    date = datetime.now()
    f.write(date.strftime("%d/%m/%Y %H:%M:%S") + " Server stopped...\n\n")
#Serialization map
map.serializationMap()
map.serializationRessources()
sys.exit(0)
