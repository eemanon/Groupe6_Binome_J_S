from socket import *
import sys
import json

#ip = localhost
#port = 9021

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <ip> <port>", file=sys.stderr)
    sys.exit(1)

SERVER = sys.argv[1]
PORT = int(sys.argv[2])
TAILLE_TAMPON = 256


with socket(AF_INET, SOCK_DGRAM) as sock:
    while True:
        # Remarque : pas besoin de bind car le port local est choisi par le système
        mess = input("Entrez une commande (help pour la liste, quit pour quitter) : ")

        # Envoi de la requête au serveur (ip, port) après encodage de str en bytes
        if mess == "quit" :
            sock.sendto(mess.encode(), (sys.argv[1], int(sys.argv[2])))
            break
        sock.sendto(mess.encode(), (sys.argv[1], int(sys.argv[2])))

        # Réception de la réponse du serveur et décodage de bytes en str
        reponse, _ = sock.recvfrom(TAILLE_TAMPON)
        print("Réponse = " + reponse.decode())
