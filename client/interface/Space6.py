from interface import Ui_Dialog
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QApplication, QItemSelectionModel, QStandardItem, QStandardItemModel
from socket import *
import sys, json, threading, time


class Interface(QtGui.QWidget, Ui_Dialog):
    
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.setupUi(self)
        
    @QtCore.pyqtSlot()
    # boutton ENVOYER
    def on_pushButton_clicked(self):
        if self.plainTextEdit.toPlainText() != "":
            item = self.plainTextEdit.toPlaintText()
            #self.textBrowser.appendPlainText(item)     TO DO : afficher la commande dans le textBrowser
            self.plainTextEdit.setPlainText("")
    
    @QtCore.pyqtSlot()
    #boutton UP
    def on_pushButton_2_clicked(self):
        #TO DO : envois la commande UP
            
    @QtCore.pyqtSlot()
    #boutton LEFT
    def on_pushButton_3_clicked(self):
        #TO DO : envois la commande LEFT
            
    @QtCore.pyqtSlot()
    #boutton DOWN
    def on_pushButton_4_clicked(self):
        #TO DO : envois la commande DOWN
            
    @QtCore.pyqtSlot()
    #boutton RIGHT
    def on_pushButton_5_clicked(self):
        #TO DO : envois la commande RIGHT
            
    @QtCore.pyqtSlot()
    #boutton PAUSE
    def on_radioButton_clicked(self):
        #TO DO : envois la commande PAUSE
            
    @QtCore.pyqtSlot()
    def on_plainTextEdit_textChanged(self):
        if str(self.plainTextEdit.toPlainText()[-1:] == '\n':
            self.plainTextEdit.setPlainText(self.plainTextEdit.toPlainText()[-1:]
            self.on_pushButton_clicked()
            
    #TO DO : AFFICHER LA CARTE DANS LE tableView
            
    
        
class ListenThread(threading.Thread):
    
    """ Creation d'un thread pour l'ecoute du serveur"""
    
    def __init__(self, sock, lock, event):
        threading.Thread.__init__(self)
        self.lock = lock
        self.sock = sock
        self.event = event
        
    def run(self):
        while not self.event.is_set():
            with self.lock:
                try:
                    reponse = self.sock.recv(TAILLE_TAMPON)
                    #return ("Reponse = " + reponse.decode())  TO DO : afficherla reponse dans le textBrowser
                except:
                    pass

#Tentative de creation d'une classe pour la connexion au serveur reprenant ../client.py                    
""""class Client(socket.socket, threading.Thread):

    def __init__(self):
        socket.socket.__init__(self)
        threading.Thread.__init__(self)
        
        self.SERVER = "localhost"
        self.PORT = 8001
        self.TAILLE_TAMPON = 10240
        self.event_stop = threading.Event()
        self.lock_thread = threading.Lock()
        
        self.sock = socket.socket(AF_INET, SOCK_STREAM)
        self.sock.connect((SERVER, PORT))
        self.sock.setblocking(0)
        
            rep = ListenThread(sock, lock_thread, event_stop)
    rep.start()
    
    print(f"Connexion vers {SERVER} : {str(PORT)} reussie.")    
    print("Entrez les commandes : ")

    while True:

        msg = input()       

        # Envoi de la requête au serveur après encodage de str en bytes
        
        with lock_thread:
            if msg == "quit" :
                sock.send(msg.upper().encode())
                event_stop.set()
                break
                
            else: 
                sock.send(msg.upper().encode())
                time.sleep(0.3)
                
    print ("Deconnexion.")
    sock.close()    
"""
		 
if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)
	win = Interface()
	win.show()
	sys.exit(app.exec_())
