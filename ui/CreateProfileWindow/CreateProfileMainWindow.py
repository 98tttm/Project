# Form implementation generated from reading ui file 'D:\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\ui\CreateProfileWindow\CreateProfileMainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.8.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1229, 842)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(80, 80, 1021, 621))
        font = QtGui.QFont()
        font.setFamily("Rockwell")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.groupBox.setTitle("")
        self.groupBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.groupBox.setObjectName("groupBox")
        self.pushButtonLogin = QtWidgets.QPushButton(parent=self.groupBox)
        self.pushButtonLogin.setGeometry(QtCore.QRect(120, 420, 361, 41))
        font = QtGui.QFont()
        font.setFamily("Lato Black")
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonLogin.setFont(font)
        self.pushButtonLogin.setStyleSheet("background-color: rgb(0, 170, 255);\n"
"background-color: rgb(255, 0, 0);\n"
"color: rgb(255, 255, 255);")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\CreateProfileWindow\\../../../Downloads/6372974_account_avatar_log in_login_register_icon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButtonLogin.setIcon(icon)
        self.pushButtonLogin.setObjectName("pushButtonLogin")
        self.label = QtWidgets.QLabel(parent=self.groupBox)
        self.label.setGeometry(QtCore.QRect(110, 170, 341, 41))
        font = QtGui.QFont()
        font.setFamily("Lato Black")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.label_5 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(530, 110, 491, 411))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setStyleSheet("")
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\CreateProfileWindow\\../../../ADMIN/Downloads/54861b4d51699454df92b8c44c44d64f.png"))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("label_5")
        self.pushButton_3 = QtWidgets.QPushButton(parent=self.groupBox)
        self.pushButton_3.setGeometry(QtCore.QRect(120, 260, 351, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_3.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("D:\\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\\ui\\CreateProfileWindow\\../../../ADMIN/Downloads/134229_cloud_guardar_save_store_up_icon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton_3.setIcon(icon1)
        self.pushButton_3.setObjectName("pushButton_3")
        self.label_2 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(130, 330, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setItalic(True)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.lineEditUsername_3 = QtWidgets.QLineEdit(parent=self.groupBox)
        self.lineEditUsername_3.setGeometry(QtCore.QRect(120, 330, 361, 51))
        self.lineEditUsername_3.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.lineEditUsername_3.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 255);")
        self.lineEditUsername_3.setText("")
        self.lineEditUsername_3.setPlaceholderText("")
        self.lineEditUsername_3.setObjectName("lineEditUsername_3")
        self.label_4 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(440, 390, 55, 16))
        self.label_4.setObjectName("label_4")
        self.label_12 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_12.setGeometry(QtCore.QRect(820, 90, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.lineEditUsername_3.raise_()
        self.pushButtonLogin.raise_()
        self.label.raise_()
        self.label_5.raise_()
        self.pushButton_3.raise_()
        self.label_2.raise_()
        self.label_4.raise_()
        self.label_12.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1229, 26))
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
        self.pushButtonLogin.setText(_translate("MainWindow", "Continue"))
        self.label.setText(_translate("MainWindow", "Create your profile"))
        self.pushButton_3.setText(_translate("MainWindow", "Upload your photo"))
        self.label_2.setText(_translate("MainWindow", "Your name:"))
        self.label_4.setText(_translate("MainWindow", "0/255"))
        self.label_12.setText(_translate("MainWindow", "Step 1 of 2"))
