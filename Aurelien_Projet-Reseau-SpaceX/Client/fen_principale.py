# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'projet_reseau.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(766, 440)
        Form.setMinimumSize(QtCore.QSize(766, 440))
        Form.setMaximumSize(QtCore.QSize(766, 440))
        Form.setSizeIncrement(QtCore.QSize(0, 0))
        self.up = QtGui.QPushButton(Form)
        self.up.setGeometry(QtCore.QRect(560, 340, 51, 41))
        self.up.setIconSize(QtCore.QSize(16, 16))
        self.up.setObjectName(_fromUtf8("up"))
        self.down = QtGui.QPushButton(Form)
        self.down.setGeometry(QtCore.QRect(560, 390, 51, 41))
        self.down.setObjectName(_fromUtf8("down"))
        self.left = QtGui.QPushButton(Form)
        self.left.setGeometry(QtCore.QRect(500, 390, 51, 41))
        self.left.setObjectName(_fromUtf8("left"))
        self.right = QtGui.QPushButton(Form)
        self.right.setGeometry(QtCore.QRect(620, 390, 51, 41))
        self.right.setObjectName(_fromUtf8("right"))
        self.carte = QtGui.QTableWidget(Form)
        self.carte.setGeometry(QtCore.QRect(10, 10, 481, 421))
        self.carte.setSizeIncrement(QtCore.QSize(0, 0))
        self.carte.setObjectName(_fromUtf8("carte"))
        self.carte.setColumnCount(0)
        self.carte.setRowCount(0)
        self.label_pseudo = QtGui.QLabel(Form)
        self.label_pseudo.setGeometry(QtCore.QRect(502, 120, 61, 17))
        self.label_pseudo.setObjectName(_fromUtf8("label_pseudo"))
        self.connexion = QtGui.QPushButton(Form)
        self.connexion.setGeometry(QtCore.QRect(642, 120, 121, 41))
        self.connexion.setObjectName(_fromUtf8("connexion"))
        self.edit_pseudo = QtGui.QLineEdit(Form)
        self.edit_pseudo.setGeometry(QtCore.QRect(502, 140, 131, 21))
        self.edit_pseudo.setObjectName(_fromUtf8("edit_pseudo"))
        self.msg_serv = QtGui.QTextBrowser(Form)
        self.msg_serv.setGeometry(QtCore.QRect(500, 10, 256, 101))
        self.msg_serv.setObjectName(_fromUtf8("msg_serv"))
        self.run = QtGui.QPushButton(Form)
        self.run.setGeometry(QtCore.QRect(680, 400, 81, 27))
        self.run.setObjectName(_fromUtf8("run"))
        self.pause = QtGui.QPushButton(Form)
        self.pause.setGeometry(QtCore.QRect(680, 370, 81, 27))
        self.pause.setObjectName(_fromUtf8("pause"))
        self.transfert = QtGui.QPushButton(Form)
        self.transfert.setGeometry(QtCore.QRect(630, 340, 131, 27))
        self.transfert.setObjectName(_fromUtf8("transfert"))
        self.pseudo = QtGui.QLabel(Form)
        self.pseudo.setGeometry(QtCore.QRect(502, 170, 131, 21))
        self.pseudo.setText(_fromUtf8(""))
        self.pseudo.setObjectName(_fromUtf8("pseudo"))
        self.changer_pseudo = QtGui.QPushButton(Form)
        self.changer_pseudo.setGeometry(QtCore.QRect(640, 170, 121, 27))
        self.changer_pseudo.setObjectName(_fromUtf8("changer_pseudo"))
        self.label_ressources = QtGui.QLabel(Form)
        self.label_ressources.setGeometry(QtCore.QRect(500, 230, 161, 17))
        self.label_ressources.setObjectName(_fromUtf8("label_ressources"))
        self.text_ressources = QtGui.QTextBrowser(Form)
        self.text_ressources.setGeometry(QtCore.QRect(500, 250, 261, 31))
        self.text_ressources.setObjectName(_fromUtf8("text_ressources"))
        self.label_joueurs = QtGui.QLabel(Form)
        self.label_joueurs.setGeometry(QtCore.QRect(500, 280, 141, 17))
        self.label_joueurs.setObjectName(_fromUtf8("label_joueurs"))
        self.text_joueurs = QtGui.QTextBrowser(Form)
        self.text_joueurs.setGeometry(QtCore.QRect(500, 300, 261, 31))
        self.text_joueurs.setObjectName(_fromUtf8("text_joueurs"))
        self.x = QtGui.QLabel(Form)
        self.x.setGeometry(QtCore.QRect(500, 200, 21, 17))
        self.x.setObjectName(_fromUtf8("x"))
        self.edit_x = QtGui.QLineEdit(Form)
        self.edit_x.setGeometry(QtCore.QRect(520, 200, 31, 21))
        self.edit_x.setObjectName(_fromUtf8("edit_x"))
        self.y = QtGui.QLabel(Form)
        self.y.setGeometry(QtCore.QRect(560, 200, 21, 17))
        self.y.setObjectName(_fromUtf8("y"))
        self.edit_y = QtGui.QLineEdit(Form)
        self.edit_y.setGeometry(QtCore.QRect(580, 200, 31, 21))
        self.edit_y.setObjectName(_fromUtf8("edit_y"))
        self.ajouter_robot = QtGui.QPushButton(Form)
        self.ajouter_robot.setGeometry(QtCore.QRect(618, 200, 141, 27))
        self.ajouter_robot.setObjectName(_fromUtf8("ajouter_robot"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Projet_Reseau", None))
        self.up.setText(_translate("Form", "↑", None))
        self.down.setText(_translate("Form", "↓", None))
        self.left.setText(_translate("Form", "←", None))
        self.right.setText(_translate("Form", "→", None))
        self.label_pseudo.setText(_translate("Form", "Pseudo :", None))
        self.connexion.setText(_translate("Form", "Connexion", None))
        self.run.setText(_translate("Form", "run", None))
        self.pause.setText(_translate("Form", "pause", None))
        self.transfert.setText(_translate("Form", "Transfert", None))
        self.changer_pseudo.setText(_translate("Form", "Changer pseudo", None))
        self.label_ressources.setText(_translate("Form", "Ressources collectées :", None))
        self.label_joueurs.setText(_translate("Form", "Joueurs connectés :", None))
        self.x.setText(_translate("Form", "x :", None))
        self.y.setText(_translate("Form", "y :", None))
        self.ajouter_robot.setText(_translate("Form", "Ajouter robot", None))

