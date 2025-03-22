from PyQt6.QtWidgets import QApplication, QMainWindow

from ui.AddProjectWindow.AddProjectWindowNewExt import AddProjectWindowNewExt

app=QApplication([])
mainwindow=QMainWindow()
myui=AddProjectWindowNewExt()
myui.setupUi(mainwindow)
myui.showWindow()
app.exec()
