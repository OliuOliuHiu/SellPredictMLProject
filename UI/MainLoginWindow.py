from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QLineEdit

from Connectors.AdminConnector import AdminConnector
from UI.FINAL_LOGIN import Ui_MainWindow
from UI.MainProgramWindowExt import MainProgramWindowExt

class LoginMainWindowExt(Ui_MainWindow):
    def __init__(self):
        self.adconnector = AdminConnector()
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.SetupSignalAndSlot()
    def showWindow(self):
        self.MainWindow.show()

    def SetupSignalAndSlot(self):
        self.pushButtonLogin.clicked.connect(self.solve_signIN)
        self.ckbShow.toggled.connect(self.toggle_password_visibility)

    def toggle_password_visibility(self):
        if self.ckbShow.isChecked():
            self.lineEditPassWord.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.lineEditPassWord.setEchoMode(QLineEdit.EchoMode.Password)  #
    def solve_signIN(self):
        try:
            username = self.lineEditUserName.text().strip()
            password = self.lineEditPassWord.text().strip()

            self.adconnector.connect()
            self.adlogin = self.adconnector.sign_in(username, password)

            if self.adlogin != None:
            # if username == 'admin' and password == '123':
                print("Successful Sign in")
                self.MainWindow.hide()
                self.mainwindow = QMainWindow()
                self.myui = MainProgramWindowExt()
                self.myui.setupUi(self.mainwindow)
                self.myui.showWindow()
            else:
                print(" Login Fail ")
                self.msg = QMessageBox()
                self.msg.setWindowTitle('Login Fail')
                self.msg.setText('Incorrect UserName or Password, Please try again')
                self.msg.setIcon(QMessageBox.Icon.Critical)
                self.msg.exec()
        except Exception as e:
            print(f" Occur Error: {e}")

