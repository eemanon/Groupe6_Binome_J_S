from PyQt4 import QtGui, QtCore
from fen_principale import Ui_Form
from socket import *
import sys
import json

class ImgWidget(QtGui.QLabel):
	def __init__(self, path, parent=None):
		super(ImgWidget, self).__init__(parent)
		pic = QtGui.QPixmap(path)
		self.setPixmap(pic)

class MajQt(QtGui.QWidget, Ui_Form):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.setupUi(self)
		if sys.argv[3] == "tcp":
			self.sock = socket(AF_INET,SOCK_STREAM)
			self.sock.connect((sys.argv[1],int(sys.argv[2])))
		if sys.argv[3] == "udp":
			self.sock = socket(AF_INET,SOCK_DGRAM)
	
	def charger_map(self, mapjson):
		self.map = json.loads(mapjson)
		self.carte.setColumnCount(self.map["dimensions"][0])
		self.carte.setRowCount(self.map["dimensions"][1])
		for x in range(self.map["dimensions"][0]):
			self.carte.setColumnWidth(x, 50)
		for y in range(self.map["dimensions"][1]):
			self.carte.setRowHeight(y, 40)
		self.carte.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		self.carte.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
		self.carte.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
		self.carte.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
		elements_bloquants = self.map["blockingElements"]
		for element in elements_bloquants:
			self.carte.setItem(element["y"],element["x"],QtGui.QTableWidgetItem(element["name"]))
			if element["name"] == "Rock":
				self.carte.setCellWidget(element["y"],element["x"],ImgWidget("images/rock.png"))
		ressources = self.map["ressources"]
		for ressource in ressources:
			self.carte.setItem(ressource["y"],ressource["x"],QtGui.QTableWidgetItem(ressource["name"]))
			if ressource["name"] == "Gold":
				self.carte.setCellWidget(ressource["y"],ressource["x"],ImgWidget("images/gold.png"))
			if ressource["name"] == "Diamant":
				self.carte.setCellWidget(ressource["y"],ressource["x"],ImgWidget("images/diamond.png"))
		robots = self.map["robots"]
		for robot in robots:
			self.carte.setItem(robot["y"],robot["x"],QtGui.QTableWidgetItem(robot["name"]))
			if robot["name"] == self.pseudo.text().upper():
				self.carte.setCellWidget(robot["y"],robot["x"],ImgWidget("images/atlas.png"))
			else:
				self.carte.setCellWidget(robot["y"],robot["x"],ImgWidget("images/p_body.png"))
	
	def charger_info(self):
		commande = "INFO"
		if sys.argv[3] == "udp":
			self.sock.sendto(commande.encode(), (sys.argv[1], int(sys.argv[2])))
			reponse, _ = self.sock.recvfrom(1028)
		if sys.argv[3] == "tcp":
			self.sock.send(commande.encode())
			reponse = self.sock.recv(1028)
		if "200" == reponse.decode().split(" ")[0]:
			infojson = reponse.decode().split(" ",1)[1]
			info = json.loads(infojson)
			self.text_ressources.setText(', '.join(info["Ressources"]))
			self.text_joueurs.setText(', '.join(info["Users"]))
	
	def update_map(self):
		commande = "UPDATE"
		if sys.argv[3] == "udp":
			self.sock.sendto(commande.encode(), (sys.argv[1], int(sys.argv[2])))
			reponse, _ = self.sock.recvfrom(1028)
		if sys.argv[3] == "tcp":
			self.sock.send(commande.encode())
			reponse = self.sock.recv(1028)
		if "100" == reponse.decode().split(" ")[0]:
			mapjson = reponse.decode().split(" ",1)[1]
			self.map = json.loads(mapjson)
			while self.carte.rowCount() > 0:
				self.carte.removeRow(0)
			self.carte.setRowCount(self.map["dimensions"][1])
			for y in range(self.map["dimensions"][1]):
				self.carte.setRowHeight(y, 40)
			self.carte.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
			self.carte.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
			self.carte.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
			elements_bloquants = self.map["blockingElements"]
			for element in elements_bloquants:
				self.carte.setItem(element["y"],element["x"],QtGui.QTableWidgetItem(element["name"]))
				if element["name"] == "Rock":
					self.carte.setCellWidget(element["y"],element["x"],ImgWidget("images/rock.png"))
			ressources = self.map["ressources"]
			for ressource in ressources:
				self.carte.setItem(ressource["y"],ressource["x"],QtGui.QTableWidgetItem(ressource["name"]))
				if ressource["name"] == "Gold":
					self.carte.setCellWidget(ressource["y"],ressource["x"],ImgWidget("images/gold.png"))
				if ressource["name"] == "Diamant":
					self.carte.setCellWidget(ressource["y"],ressource["x"],ImgWidget("images/diamond.png"))
			robots = self.map["robots"]
			for robot in robots:
				self.carte.setItem(robot["y"],robot["x"],QtGui.QTableWidgetItem(robot["name"]))
				if robot["name"] == self.pseudo.text().upper():
					self.carte.setCellWidget(robot["y"],robot["x"],ImgWidget("images/atlas.png"))
				else:
					self.carte.setCellWidget(robot["y"],robot["x"],ImgWidget("images/p_body.png"))
	
	def sendQuit(self):
		self.sock.close()
	
	@QtCore.pyqtSlot()
	def on_connexion_clicked(self):
		self.msg_serv.setText(self.edit_pseudo.text())
		if len(sys.argv) != 4:
			print("Usage: "+sys.argv[0]+" <ip> <port> <transport>", file=sys.stderr)
			sys.exit(1)
		commande = "CONNECT "+self.edit_pseudo.text()
		if sys.argv[3] == "udp":
			self.sock.sendto(commande.encode(), (sys.argv[1], int(sys.argv[2])))
			reponse, _ = self.sock.recvfrom(1028)
		if sys.argv[3] == "tcp":
			self.sock.send(commande.encode())
			reponse = self.sock.recv(1028)
			print("LA REPONSE : "+reponse.decode())
		if "440" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Le pseudo que vous avez choisi n'est pas valide.")
			self.edit_pseudo.setText("")
		elif "450" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Le pseudo que vous avez choisi est déjà utilisé.")
			self.edit_pseudo.setText("")
		else:
			self.msg_serv.setText("Connexion réussie !")
			self.pseudo.setText(self.edit_pseudo.text())
			self.edit_pseudo.setText("")
			mapjson = reponse.decode().split(" ",1)[1]
			print(mapjson)
			self.charger_map(mapjson)
			self.charger_info()

	@QtCore.pyqtSlot()
	def on_changer_pseudo_clicked(self):
		commande = "NAME "+self.edit_pseudo.text()
		if sys.argv[3] == "udp":
			self.sock.sendto(commande.encode(), (sys.argv[1], int(sys.argv[2])))
			reponse, _ = self.sock.recvfrom(1028)
		if sys.argv[3] == "tcp":
			self.sock.send(commande.encode())
			reponse = self.sock.recv(1028)
		if "200" == reponse.decode().split(" ")[0]:
			self.pseudo.setText(self.edit_pseudo.text())
			self.msg_serv.setText("Pseudo changé.")
			self.edit_pseudo.setText("")
			self.charger_info()
			self.update_map()
		if "480" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Impossible de changer le pseudo.")
			self.edit_pseudo.setText("")
	
	@QtCore.pyqtSlot()
	def on_ajouter_robot_clicked(self):
		commande = "ADD ("+str(int(self.edit_x.text())-1)+","+str(int(self.edit_y.text())-1)+")"
		if sys.argv[3] == "udp":
			self.sock.sendto(commande.encode(), (sys.argv[1], int(sys.argv[2])))
			reponse, _ = self.sock.recvfrom(1028)
		if sys.argv[3] == "tcp":
			self.sock.send(commande.encode())
			reponse = self.sock.recv(1028)
		if "210" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Robot ajouté !")
			self.edit_x.setText("")
			self.edit_y.setText("")
		if "430" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Impossible d'ajouter le robot aux coordonnées indiquées.")
			self.edit_x.setText("")
			self.edit_y.setText("")

	@QtCore.pyqtSlot()
	def on_up_clicked(self):
		commande = "DOWN"
		if sys.argv[3] == "udp":
			self.sock.sendto(commande.encode(), (sys.argv[1], int(sys.argv[2])))
			reponse, _ = self.sock.recvfrom(1028)
		if sys.argv[3] == "tcp":
			self.sock.send(commande.encode())
			reponse = self.sock.recv(1028)
		if "270" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Déplacement vers le haut effectué.")
			self.update_map()
		if "480" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Déplacement impossible.")
	
	@QtCore.pyqtSlot()
	def on_right_clicked(self):
		commande = "RIGHT"
		if sys.argv[3] == "udp":
			self.sock.sendto(commande.encode(), (sys.argv[1], int(sys.argv[2])))
			reponse, _ = self.sock.recvfrom(1028)
		if sys.argv[3] == "tcp":
			self.sock.send(commande.encode())
			reponse = self.sock.recv(1028)
		if "270" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Déplacement vers la droite effectué.")
			self.update_map()
		if "480" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Déplacement impossible.")
	
	@QtCore.pyqtSlot()
	def on_down_clicked(self):
		commande = "UP"
		if sys.argv[3] == "udp":
			self.sock.sendto(commande.encode(), (sys.argv[1], int(sys.argv[2])))
			reponse, _ = self.sock.recvfrom(1028)
		if sys.argv[3] == "tcp":
			self.sock.send(commande.encode())
			reponse = self.sock.recv(1028)
		if "270" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Déplacement vers le bas effectué.")
			self.update_map()
		if "480" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Déplacement impossible.")
	
	@QtCore.pyqtSlot()
	def on_left_clicked(self):
		commande = "LEFT"
		if sys.argv[3] == "udp":
			self.sock.sendto(commande.encode(), (sys.argv[1], int(sys.argv[2])))
			reponse, _ = self.sock.recvfrom(1028)
		if sys.argv[3] == "tcp":
			self.sock.send(commande.encode())
			reponse = self.sock.recv(1028)
		if "270" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Déplacement vers la gauche effectué.")
			self.update_map()
		if "480" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Déplacement impossible.")
	
	@QtCore.pyqtSlot()
	def on_pause_clicked(self):
		commande = "PAUSE"
		if sys.argv[3] == "udp":
			self.sock.sendto(commande.encode(), (sys.argv[1], int(sys.argv[2])))
			reponse, _ = self.sock.recvfrom(1028)
		if sys.argv[3] == "tcp":
			self.sock.send(commande.encode())
			reponse = self.sock.recv(1028)
		if "250" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Le robot a été mis en pause.")
		if "480" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Mise en pause impossible.")
	
	@QtCore.pyqtSlot()
	def on_run_clicked(self):
		commande = "RUN"
		if sys.argv[3] == "udp":
			self.sock.sendto(commande.encode(), (sys.argv[1], int(sys.argv[2])))
			reponse, _ = self.sock.recvfrom(1028)
		if sys.argv[3] == "tcp":
			self.sock.send(commande.encode())
			reponse = self.sock.recv(1028)
		if "260" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Le robot peut reprendre son déplacement.")
		if "480" == reponse.decode().split(" ")[0]:
			self.msg_serv.setText("Lancement impossible.")

	"""	
	@QtCore.pyqtSlot()
	def on_transfert_clicked(self):
		#code pour le transfert"""

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	win = MajQt()
	win.show()
	sys.exit(app.exec_())
	