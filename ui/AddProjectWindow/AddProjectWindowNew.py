# Form implementation generated from reading ui file 'D:\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\ui\AddProjectWindow\AddProjectWindowNew.ui'
#
# Created by: PyQt6 UI code generator 6.8.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1363, 942)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox.setEnabled(True)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 1381, 891))
        font = QtGui.QFont()
        font.setFamily("Rockwell")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.groupBox.setTitle("")
        self.groupBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(parent=self.groupBox)
        self.label.setGeometry(QtCore.QRect(140, 20, 311, 61))
        font = QtGui.QFont()
        font.setFamily("Lato Black")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("color: rgb(255, 0, 0);\n"
"color: rgb(255, 0, 0);\n"
"color: rgb(0, 0, 0);")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(parent=self.groupBox)
        self.pushButton.setGeometry(QtCore.QRect(50, 20, 101, 61))
        self.pushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../../Image/file_7222904.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(50, 50))
        self.pushButton.setObjectName("pushButton")
        self.lineEditProjectName = QtWidgets.QLineEdit(parent=self.groupBox)
        self.lineEditProjectName.setGeometry(QtCore.QRect(50, 90, 651, 41))
        font = QtGui.QFont()
        font.setItalic(True)
        self.lineEditProjectName.setFont(font)
        self.lineEditProjectName.setStyleSheet("")
        self.lineEditProjectName.setText("")
        self.lineEditProjectName.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.lineEditProjectName.setObjectName("lineEditProjectName")
        self.lineEditManager = QtWidgets.QLineEdit(parent=self.groupBox)
        self.lineEditManager.setGeometry(QtCore.QRect(50, 160, 651, 41))
        font = QtGui.QFont()
        font.setItalic(True)
        self.lineEditManager.setFont(font)
        self.lineEditManager.setStyleSheet("")
        self.lineEditManager.setText("")
        self.lineEditManager.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.lineEditManager.setObjectName("lineEditManager")
        self.comboBoxStatus = QtWidgets.QComboBox(parent=self.groupBox)
        self.comboBoxStatus.setGeometry(QtCore.QRect(520, 720, 171, 41))
        self.comboBoxStatus.setStyleSheet("background-color: rgb(0, 0, 0);\n"
"color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);")
        self.comboBoxStatus.setObjectName("comboBoxStatus")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../../Image/folder_2635178.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.comboBoxStatus.addItem(icon1, "")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../../Image/clock_3801836.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.comboBoxStatus.addItem(icon2, "")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../../Image/u-turn_16338815.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.comboBoxStatus.addItem(icon3, "")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../../Image/check_4049778.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.comboBoxStatus.addItem(icon4, "")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../../Image/calendar_11019109.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.comboBoxStatus.addItem(icon5, "")
        self.pushButtonAdd = QtWidgets.QPushButton(parent=self.groupBox)
        self.pushButtonAdd.setGeometry(QtCore.QRect(140, 720, 171, 41))
        font = QtGui.QFont()
        font.setFamily("Lato Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonAdd.setFont(font)
        self.pushButtonAdd.setStyleSheet("background-color: rgb(0, 170, 255);color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 0, 0);")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("C:/Users/FPT/Downloads/6372974_account_avatar_log in_login_register_icon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButtonAdd.setIcon(icon6)
        self.pushButtonAdd.setObjectName("pushButtonAdd")
        self.label_2 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(40, 540, 100, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(410, 540, 81, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.dateTimeStartDate = QtWidgets.QDateTimeEdit(parent=self.groupBox)
        self.dateTimeStartDate.setGeometry(QtCore.QRect(140, 540, 211, 41))
        self.dateTimeStartDate.setObjectName("dateTimeStartDate")
        self.dateTimeEndDate = QtWidgets.QDateTimeEdit(parent=self.groupBox)
        self.dateTimeEndDate.setGeometry(QtCore.QRect(490, 540, 211, 41))
        self.dateTimeEndDate.setObjectName("dateTimeEndDate")
        self.pushButtonClear = QtWidgets.QPushButton(parent=self.groupBox)
        self.pushButtonClear.setGeometry(QtCore.QRect(330, 720, 171, 41))
        font = QtGui.QFont()
        font.setFamily("Lato Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonClear.setFont(font)
        self.pushButtonClear.setStyleSheet("background-color: rgb(0, 170, 255);color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 0, 0);")
        self.pushButtonClear.setIcon(icon6)
        self.pushButtonClear.setObjectName("pushButtonClear")
        self.lineEditProjectName_2 = QtWidgets.QLineEdit(parent=self.groupBox)
        self.lineEditProjectName_2.setGeometry(QtCore.QRect(50, 230, 651, 91))
        font = QtGui.QFont()
        font.setItalic(True)
        self.lineEditProjectName_2.setFont(font)
        self.lineEditProjectName_2.setStyleSheet("")
        self.lineEditProjectName_2.setText("")
        self.lineEditProjectName_2.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.lineEditProjectName_2.setObjectName("lineEditProjectName_2")
        self.comboBoxAssignee = QtWidgets.QComboBox(parent=self.groupBox)
        self.comboBoxAssignee.setGeometry(QtCore.QRect(150, 370, 551, 41))
        self.comboBoxAssignee.setObjectName("comboBoxAssignee")
        self.pushButtonAddAssignee = QtWidgets.QPushButton(parent=self.groupBox)
        self.pushButtonAddAssignee.setGeometry(QtCore.QRect(50, 480, 150, 40))
        self.pushButtonAddAssignee.setObjectName("pushButtonAddAssignee")
        self.pushButtonRemoveAssignee = QtWidgets.QPushButton(parent=self.groupBox)
        self.pushButtonRemoveAssignee.setGeometry(QtCore.QRect(210, 480, 150, 40))
        self.pushButtonRemoveAssignee.setObjectName("pushButtonRemoveAssignee")
        self.listWidgetAssignees = QtWidgets.QListWidget(parent=self.groupBox)
        self.listWidgetAssignees.setGeometry(QtCore.QRect(370, 420, 331, 100))
        self.listWidgetAssignees.setObjectName("listWidgetAssignees")
        self.label_8 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_8.setGeometry(QtCore.QRect(40, 370, 91, 41))
        font = QtGui.QFont()
        font.setFamily("Lato Black")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setStyleSheet("")
        self.label_8.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.pushButtonInfor = QtWidgets.QPushButton(parent=self.groupBox)
        self.pushButtonInfor.setGeometry(QtCore.QRect(50, 430, 311, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonInfor.setFont(font)
        self.pushButtonInfor.setStyleSheet("background-color: rgb(255, 0, 0);\n"
"color: rgb(255, 255, 255);")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../MainWindow/images/4850470_card_employee_id_identification_identity_icon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButtonInfor.setIcon(icon7)
        self.pushButtonInfor.setObjectName("pushButtonInfor")
        self.label_9 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_9.setGeometry(QtCore.QRect(0, 620, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Lato Black")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setStyleSheet("")
        self.label_9.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.pushButtonFile = QtWidgets.QPushButton(parent=self.groupBox)
        self.pushButtonFile.setGeometry(QtCore.QRect(140, 620, 561, 41))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.pushButtonFile.setFont(font)
        self.pushButtonFile.setStyleSheet("background-color: rgb(255, 0, 0);\n"
"background-color: rgb(200, 200, 200);")
        self.pushButtonFile.setObjectName("pushButtonFile")
        self.detailWidget = QtWidgets.QWidget(parent=self.groupBox)
        self.detailWidget.setEnabled(True)
        self.detailWidget.setGeometry(QtCore.QRect(739, 89, 561, 671))
        self.detailWidget.setMouseTracking(False)
        self.detailWidget.setStyleSheet("background-color: rgb(255, 0, 0);\n"
"color: rgb(255, 255, 255);")
        self.detailWidget.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhNone)
        self.detailWidget.setObjectName("detailWidget")
        self.label_10 = QtWidgets.QLabel(parent=self.detailWidget)
        self.label_10.setGeometry(QtCore.QRect(100, 50, 361, 61))
        font = QtGui.QFont()
        font.setFamily("Lato Black")
        font.setPointSize(30)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_10.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.label_7 = QtWidgets.QLabel(parent=self.detailWidget)
        self.label_7.setGeometry(QtCore.QRect(20, 160, 91, 41))
        font = QtGui.QFont()
        font.setFamily("Lato Black")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_7.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.horizontalSliderProgress = QtWidgets.QSlider(parent=self.detailWidget)
        self.horizontalSliderProgress.setGeometry(QtCore.QRect(130, 170, 371, 22))
        self.horizontalSliderProgress.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"background-color: rgb(170, 0, 0);\n"
"background-color: rgb(255, 0, 0);\n"
"background-color: rgb(213, 213, 213);")
        self.horizontalSliderProgress.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSliderProgress.setObjectName("horizontalSliderProgress")
        self.label_4 = QtWidgets.QLabel(parent=self.detailWidget)
        self.label_4.setGeometry(QtCore.QRect(30, 250, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_4.setObjectName("label_4")
        self.comboBoxPriority = QtWidgets.QComboBox(parent=self.detailWidget)
        self.comboBoxPriority.setGeometry(QtCore.QRect(130, 240, 381, 41))
        self.comboBoxPriority.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.comboBoxPriority.setObjectName("comboBoxPriority")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../../Image/army_3191032.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.comboBoxPriority.addItem(icon8, "")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../../Image/flag_777580 (1).png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.comboBoxPriority.addItem(icon9, "")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../../Image/flag_9177268.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.comboBoxPriority.addItem(icon10, "")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../../Image/red-flag_2483421.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.comboBoxPriority.addItem(icon11, "")
        self.checkBox = QtWidgets.QCheckBox(parent=self.detailWidget)
        self.checkBox.setGeometry(QtCore.QRect(40, 330, 261, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.checkBox.setFont(font)
        self.checkBox.setStyleSheet("color: rgb(255, 255, 255);")
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtWidgets.QCheckBox(parent=self.detailWidget)
        self.checkBox_2.setGeometry(QtCore.QRect(40, 380, 301, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.checkBox_2.setFont(font)
        self.checkBox_2.setStyleSheet("color: rgb(255, 255, 255);")
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_3 = QtWidgets.QCheckBox(parent=self.detailWidget)
        self.checkBox_3.setGeometry(QtCore.QRect(40, 430, 331, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.checkBox_3.setFont(font)
        self.checkBox_3.setStyleSheet("color: rgb(255, 255, 255);")
        self.checkBox_3.setObjectName("checkBox_3")
        self.label_11 = QtWidgets.QLabel(parent=self.detailWidget)
        self.label_11.setGeometry(QtCore.QRect(20, 500, 161, 41))
        font = QtGui.QFont()
        font.setFamily("Lato Black")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_11.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.detailWidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(180, 500, 331, 31))
        self.lineEdit_2.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label_12 = QtWidgets.QLabel(parent=self.detailWidget)
        self.label_12.setGeometry(QtCore.QRect(10, 570, 161, 41))
        font = QtGui.QFont()
        font.setFamily("Lato Black")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_12.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.comboBoxDependency = QtWidgets.QComboBox(parent=self.detailWidget)
        self.comboBoxDependency.setGeometry(QtCore.QRect(180, 570, 331, 41))
        self.comboBoxDependency.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.comboBoxDependency.setObjectName("comboBoxDependency")
        self.pushButtonMore = QtWidgets.QPushButton(parent=self.groupBox)
        self.pushButtonMore.setGeometry(QtCore.QRect(740, 50, 101, 28))
        self.pushButtonMore.setStyleSheet("background-color: rgb(213, 213, 213);")
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\AddProjectWindow\\../MainWindow/images/211614_down_b_arrow_icon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButtonMore.setIcon(icon12)
        self.pushButtonMore.setObjectName("pushButtonMore")
        self.pushButtonAddAssignee.raise_()
        self.pushButtonRemoveAssignee.raise_()
        self.listWidgetAssignees.raise_()
        self.pushButton.raise_()
        self.label.raise_()
        self.lineEditProjectName.raise_()
        self.lineEditManager.raise_()
        self.comboBoxStatus.raise_()
        self.pushButtonAdd.raise_()
        self.label_2.raise_()
        self.label_3.raise_()
        self.dateTimeStartDate.raise_()
        self.dateTimeEndDate.raise_()
        self.pushButtonClear.raise_()
        self.lineEditProjectName_2.raise_()
        self.comboBoxAssignee.raise_()
        self.label_8.raise_()
        self.pushButtonInfor.raise_()
        self.label_9.raise_()
        self.pushButtonFile.raise_()
        self.detailWidget.raise_()
        self.pushButtonMore.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1363, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Add new project"))
        self.lineEditProjectName.setPlaceholderText(_translate("MainWindow", "Enter your new project name..."))
        self.lineEditManager.setPlaceholderText(_translate("MainWindow", "Who is Project\'s Manager?"))
        self.comboBoxStatus.setItemText(0, _translate("MainWindow", "Open"))
        self.comboBoxStatus.setItemText(1, _translate("MainWindow", "Pending"))
        self.comboBoxStatus.setItemText(2, _translate("MainWindow", "Ongoing"))
        self.comboBoxStatus.setItemText(3, _translate("MainWindow", "Completed"))
        self.comboBoxStatus.setItemText(4, _translate("MainWindow", "Canceled"))
        self.pushButtonAdd.setText(_translate("MainWindow", "Add"))
        self.label_2.setText(_translate("MainWindow", "Start Date:"))
        self.label_3.setText(_translate("MainWindow", "End Date:"))
        self.pushButtonClear.setText(_translate("MainWindow", "Clear"))
        self.lineEditProjectName_2.setPlaceholderText(_translate("MainWindow", "Enter your task description..."))
        self.pushButtonAddAssignee.setText(_translate("MainWindow", "Add Assignee"))
        self.pushButtonRemoveAssignee.setText(_translate("MainWindow", "Remove Assignee"))
        self.label_8.setText(_translate("MainWindow", "Assignee:"))
        self.pushButtonInfor.setText(_translate("MainWindow", "Information of Assignee"))
        self.label_9.setText(_translate("MainWindow", "File:"))
        self.pushButtonFile.setText(_translate("MainWindow", "Attach file here..."))
        self.label_10.setText(_translate("MainWindow", "MORE DETAIL:"))
        self.label_7.setText(_translate("MainWindow", "Status:"))
        self.label_4.setText(_translate("MainWindow", "Priority:"))
        self.comboBoxPriority.setItemText(0, _translate("MainWindow", "Priority 1"))
        self.comboBoxPriority.setItemText(1, _translate("MainWindow", "Priority 2"))
        self.comboBoxPriority.setItemText(2, _translate("MainWindow", "Priority 3"))
        self.comboBoxPriority.setItemText(3, _translate("MainWindow", "Priority 4"))
        self.checkBox.setText(_translate("MainWindow", "View Gantt Chart"))
        self.checkBox_2.setText(_translate("MainWindow", "View Kanban Board"))
        self.checkBox_3.setText(_translate("MainWindow", "Drag-and-drop status"))
        self.label_11.setText(_translate("MainWindow", "Estimated time:"))
        self.label_12.setText(_translate("MainWindow", "Dependency:"))
        self.pushButtonMore.setText(_translate("MainWindow", "View more"))
