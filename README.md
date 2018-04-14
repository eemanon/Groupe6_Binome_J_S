Projet Reseau Space6

# Presentation

Projet propose par Eric JACOBONI et Elsy KADDOUM dans le cadre de l'UE MID0601V de la L3 MIASHS parcours Informatiques de l'Universite Jean Jaures.

Realise par Jonathan FERNANDO-JOHNSON et Sebastian SIMON.

Dans le cadre d’une simulation de comportements de robots, nous souhaitons mettre en place un
serveur gerant une carte contenant des ressources. Des clients se connectent sur le serveur afin de
tester le comportement de leur robot (1 robot/client). Le comportement du robot consiste a explorer
la carte tout en indiquant sa position et les ressources recuperees.

# Lancer le serveur

Lancer dans une console le fichier ./server/threading_server.py avec python. 
Un port d'ecoute autre que celui par defaut (port : 9021 definit dans le fichier de configuration ./server/spaceXserver.conf) peut etre passe en parametre.

	$python threading_server.py <port>
	
# Lancer l'interface client

Lancer dans une console le fichier ./client/Space6.py avec python.
Le client ecoute par defaut le serveur en local. L'adresse du serveur peut etre modifier directement dans le fichier de configuration ./client/spaceX.conf .
Un port d'ecoute autre que celui par defaut (port : 9021 definit dans le fichier de configuration ./client/spaceX.conf) peut etre passe en parametre.

	$python ./client/Space6.py <port>
	
# Commandes client

Une fois le serveur puis l'interface client lances, l'utilisateur dipose de differentes commandes qui doit entrer dans l'interface (voir ci-dessous) 
pour gerer le comportement de son robot.

	. CONNECT [NomDuRobot]	:	connexion au serveur
	. ADD (X,Y) 			:	ajout du robot sur la carte aux coordonnees (abscisse = X, ordonnee = Y)
	. UP					:	deplace le robot vers le haut
	. DOWN					:	deplace le robot vers le bas
	. LEFT					:	deplace le robot vers la gauche
	. RIGHT					:	deplace le robot vers la droite
	. PAUSE					:	met le robot en pause
	. RUN					:	redemare le robot apres qu'il ait ete mis en pause
	. INFO					:	affiche les ressources collectees par le robot et le nom des autres client connectes au serveur
	. QUIT					:	deconnexion au serveur