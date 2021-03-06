# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets

from client import *

class Ui_MainWindow(object):
    def clicked(self):
        processedCommand(self.lineEdit.text())
        res = getReponse()
        self.textBrowser.append (res)
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(629, 536)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setInputMask("")
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.submitcommand = QtWidgets.QPushButton(self.centralwidget)
        self.submitcommand.setObjectName("submitcommand")
        self.verticalLayout.addWidget(self.submitcommand)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 629, 22))
        self.menubar.setObjectName("menubar")
        self.menuFTP_APPLICATION = QtWidgets.QMenu(self.menubar)
        self.menuFTP_APPLICATION.setObjectName("menuFTP_APPLICATION")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuFTP_APPLICATION.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.lineEdit.setText(_translate("MainWindow", "command"))
        self.submitcommand.setText(_translate("MainWindow", "submit"))
        self.menuFTP_APPLICATION.setTitle(_translate("MainWindow", "FTP APPLICATION"))
        self.submitcommand.clicked.connect(self.clicked)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
