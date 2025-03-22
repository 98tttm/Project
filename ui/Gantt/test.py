from PyQt6.QtWidgets import QApplication, QMainWindow

from ui.Gantt.GanttChartWindowExt import GanttChartWindowExt

app=QApplication([])
mainwindow=QMainWindow()
myui=GanttChartWindowExt()
myui.setupUi(mainwindow)
myui.showWindow()
app.exec()
