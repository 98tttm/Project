from ui.TermAndCoditionsWindow.TermAndCoditionsWindow import Ui_MainWindow


class TermAndCoditionsWindowExt(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

    def showWindow(self):
        self.MainWindow.show()