from PyQt6.QtWidgets import QApplication, QMainWindow

from ui.InformationAssigneeWindow.AssingeeMainWindowExt import AssigneeMainWindowExt

app=QApplication([])
mainwindow=QMainWindow()
myui=AssigneeMainWindowExt()
myui.setupUi(mainwindow)
myui.showWindow()
app.exec()