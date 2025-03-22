from PyQt6.QtWidgets import QApplication, QMainWindow

from ui_test.AddProjectWindowTest.AddProjectWindowTestExt import AddProjectWindowTestExt

app=QApplication([])
mainwindow=QMainWindow()
myui=AddProjectWindowTestExt()
myui.setupUi(mainwindow)
myui.showWindow()
app.exec()