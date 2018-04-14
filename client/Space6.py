from interface import Ui_Dialog
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from socket import *
import sys, json, threading, time


class Interface(QtGui.QWidget, Ui_Dialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        config = loadConfig()
        self.client = Client(self)

    @QtCore.pyqtSlot()
    # boutton ENVOYER
    def on_pushButton_clicked(self):
        if self.plainTextEdit.toPlainText() != "":
            commande = str(self.plainTextEdit.toPlainText())
            self.textBrowser.setText("C: " + commande)  # affiche la commande dans le textBrowser
            self.plainTextEdit.clear()
            reponse = str(self.client.sendCmd(commande).decode())
            rep = reponse.split(" ", 1)

            if commande.split(" ", 1)[0] == "connect":
                if rep[0] == "200":
                    self.textBrowser.setText("Connetion successful")
                    mapjson = rep[1]
                    self.printMap(json.loads(mapjson))
                else:
                    self.textBrowser.setText(rep[1])

            elif commande.split(" ", 1)[0] == "info":
                self.textBrowser.setText(rep[1])

            elif commande.split(" ", 1)[0] == "add":
                repOk = reponse.split(" ", 4)
                if repOk[0] == "210":
                    self.textBrowser.setText(commande.upper() + " : Robot is added ")
                    mapjson = repOk[4]
                    self.printMap(json.loads(mapjson))
                else:
                    self.textBrowser.setText(rep[1])

            else:
                self.textBrowser.setText(rep[0] + " " + rep[1])

    @QtCore.pyqtSlot()
    def on_pushButton_2_clicked(self):
        """Boutton Up : deplace le robot vers le haut """
        self.textBrowser.setText("C: UP")  # affiche la commande dans le textBrowser
        self.moveBoutton("up")

    @QtCore.pyqtSlot()
    def on_pushButton_3_clicked(self):
        """Boutton Left : deplace le robot vers la gauche"""
        self.textBrowser.setText("C: LEFT")  # affiche la commande dans le textBrowser
        self.moveBoutton("left")

    @QtCore.pyqtSlot()
    def on_pushButton_4_clicked(self):
        """Boutton Down : deplace le robot vers le bas """
        self.textBrowser.setText("C: DOWN")  # affiche la commande dans le textBrowser
        self.moveBoutton("down")

    @QtCore.pyqtSlot()
    def on_pushButton_5_clicked(self):
        """Boutton Right : deplace le robot vers la droite """
        self.textBrowser.setText("C: RIGHT")  # affiche la commande dans le textBrowser
        self.moveBoutton("right")

    @QtCore.pyqtSlot()
    def on_radioButton_pressed(self):
        """Boutton Pause : place le robot en pause """
        self.textBrowser.setText("C: PAUSE")  # affiche la commande dans le textBrowser
        rep = self.client.sendCmd("pause").decode()
        self.textBrowser.setText("Reponse : " + rep)

    @QtCore.pyqtSlot()
    def on_radioButton_released(self):
        """Boutton Run : relance le robot si ce dernier est en pause """
        self.textBrowser.setText("C: RUN")  # affiche la commande dans le textBrowser
        rep = self.client.sendCmd("run").decode()
        self.textBrowser.setText("Reponse : " + rep)

    def printMap(self, map):
        """Ajout de la carte a l'interface"""
        img2 = QImage(self.mapToImage(map, (255, 255, 102)))
        pixmap2 = QPixmap.fromImage(img2)
        pixmap2 = pixmap2.scaledToWidth(self.label.width())
        pixmap2 = pixmap2.scaledToHeight(self.label.height())
        self.label.setPixmap(pixmap2)

    def mapToImage(self, map, baseColor):
        """
        This function maps a python object of the in RFC defined map to an image.
        """

        img = QImage(map["dimensions"][0], map["dimensions"][1], QImage.Format_RGB32);
        # clear image with black pixels before adding
        for x in range(img.width()):
            for y in range(img.height()):
                img.setPixel(x, y, qRgb(baseColor[0], baseColor[1], baseColor[2]))

        # add blocking elements - red colors
        for block in map["blockingElements"]:
            img.setPixel(block["x"], block["y"], qRgb(255, 0, 0))
        # add robots - blue colors
        for block in map["robots"]:
            img.setPixel(block["x"], block["y"], qRgb(0, 0, 255))
        # add ressources - green colors
        for block in map["ressources"]:
            img.setPixel(block["x"], block["y"], qRgb(0, 255, 0))

        # mirror image on x axis to represent up down commands...
        img = img.mirrored(horizontal=False, vertical=True)
        return img

    def moveBoutton(self, commande):
        """Envois la commande boutton passee en parametre au serveur"""
        rep = str(self.client.sendCmd(commande).decode())  # envois de la commande au serveur
        repOk = rep.split(" ", 2)
        repNon = rep.split(" ", 1)

        if repOk[0] == "270":
            self.textBrowser.setText(commande.upper() + " : " + (repOk[1].split(")")[0] + ")"))
            mapjson = repOk[2]
            self.printMap(json.loads(mapjson))
        else:
            self.textBrowser.setText(repNon[1])


class ListenThread(threading.Thread):
    """ Creation d'un thread pour l'ecoute du serveur
    Retourne la reponse de ce dernier"""

    def __init__(self, sock, lock, event, interface):
        threading.Thread.__init__(self)
        self.lock = lock
        self.sock = sock
        self.event = event

    def run(self):
        while not self.event.is_set():
            with self.lock:
                try:
                    reponse = self.sock.recv(TAILLE_TAMPON)
                    rep = reponse.decode().split(" ", 1)
                    print("rep1:" + rep[1])
                    mapjson = json.loads(rep[1])
                    interface.printMap(json.loads(mapjson))
                    return rep
                except:
                    pass


class Client(socket, threading.Thread):
    """ Creation d'une connection TCP avec le serveur"""

    def __init__(self, interface):
        conf = loadConfig()
        self.server = conf["server"]
        self.port = int(conf["port"])
        self.taille = int(conf["tailleTampon"])
        self.event_stop = threading.Event()
        self.lock_thread = threading.Lock()
        self.interface = interface
        print (self.taille)

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.server, self.port))
        self.sock.setblocking(0)

        self.rep = ListenThread(self.sock, self.lock_thread, self.event_stop, self.interface)
        self.rep.start()

        self.interface.textBrowser.setText(
            "Connexion vers " + self.server + " : " + str(self.port) + " reussie.\n\nBienvenue sur Space6")

    def sendCmd(self, commande):
        """ Envois de la commande passee en parametre au serveur
        Rentourne la reponse de ce dernier"""
        if commande.upper() == "QUIT":
            self.sendQuit()
        else:
            with self.lock_thread:
                self.sock.send(commande.upper().encode())
                time.sleep(0.3)
                reponse = self.sock.recv(self.taille)
            return reponse

    def sendQuit(self):
        """ Envois de la commande QUIT au serveur
        Deconnexion du client et du serveur"""
        msg = "quit"
        self.sock.send(msg.upper().encode())
        self.event_stop.set()
        self.rep.join()
        self.interface.textBrowser.setText("Deconnexion.")
        self.sock.close()


def loadConfig():
    """
	loads a config file. Must be of this structure:
    <property1> <value1>
    <property2> <value2>
    :return: a dictionnary of the file's content.
    The following keys are set by default: port, path
    """
    config = {"port": 9021, "server": "localhost", "tailleTampon": "10240"}
    with open("spaceX.conf", "r") as r:
        for line in r:
            conf = line.split()
            config[conf[0]] = conf[1]
    if (len(sys.argv) >= 2):
        config["port"] = sys.argv[1]
    return config


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = Interface()
    win.show()
    sys.exit(app.exec_())
