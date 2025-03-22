from PyQt6.QtWidgets import QApplication, QMainWindow
from UI.MainLoginWindow import LoginMainWindowExt

def run_app():
    app = QApplication([])
    mainwindow = QMainWindow()
    myui = LoginMainWindowExt()
    myui.setupUi(mainwindow)
    myui.showWindow()
    app.exec()

# Gọi hàm để chạy ứng dụng
if __name__ == "__main__":
    run_app()
