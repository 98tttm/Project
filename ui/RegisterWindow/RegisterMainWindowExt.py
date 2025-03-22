import os
import re
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

from Models.User import User
from libs.DataConnector import DataConnector
from ui.RegisterWindow.RegisterMainWindow import Ui_MainWindow
from ui.TermAndCoditionsWindow.TermAndCoditionsWindowExt import TermAndCoditionsWindowExt
import ui.LoginWindow.LoginMainWindowExt as login_ext


def is_valid_email(email: str) -> bool:
    """
    Basic email format check. You can use more sophisticated regex or external libraries.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone: str) -> bool:
    """
    Basic phone format check (digits only, 9-15 length). Adjust as needed.
    """
    pattern = r'^\d{9,15}$'
    return re.match(pattern, phone) is not None


class RegisterMainWindowExt(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.dc = DataConnector()
        self.users = self.dc.get_all_users()
        self.avatar_path = None  # Store the selected avatar file path

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.setupSignalAndSlot()
        self.lineEditName.setFocus()

        # If your .ui has a pushButtonUpavt and labelAvatar, connect them:
        self.pushButtonUpavt.clicked.connect(self.handle_upload_avatar)
        self.labelAvatar.setPixmap(QPixmap("D:\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\Image\avt.png"))

    def showWindow(self):
        self.MainWindow.show()

    def setupSignalAndSlot(self):
        self.pushButtonTermAndCondition.clicked.connect(self.TermAndCodition)
        self.pushButtonSignUp.clicked.connect(self.process_register)
        self.pushButtonLogin.clicked.connect(self.BackToLogin)
        self.pushButtonClear.clicked.connect(self.Clear)

    def Clear(self):
        self.lineEditName.clear()
        self.lineEditEmail.clear()
        self.lineEditPhoneNum.clear()
        self.lineEditUsername.clear()
        self.lineEditPassword.clear()
        self.lineEditConfirmPassword.clear()
        self.avatar_path = None  # Reset
        # Optionally clear the avatar display
        self.labelAvatar.clear()
        self.lineEditName.setFocus()

    def handle_upload_avatar(self):
        """
        Let the user pick an image from the file system.
        Display it in labelAvatar as a square.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self.MainWindow,
            "Select an Avatar Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.avatar_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Make a square thumbnail (200x200 for example)
                size = 200
                # Scale while preserving aspect ratio, then possibly crop center if you want a perfect square
                pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

                # If you want a perfect center-crop:
                rect = pixmap.rect()
                side = min(rect.width(), rect.height())
                crop_x = (rect.width() - side) // 2
                crop_y = (rect.height() - side) // 2
                square_pixmap = pixmap.copy(crop_x, crop_y, side, side)

                self.labelAvatar.setPixmap(square_pixmap)
                self.labelAvatar.setScaledContents(True)
            else:
                QMessageBox.warning(self.MainWindow, "Error", "Could not load the selected image.")

    def process_register(self):
        name = self.lineEditName.text().strip()
        email = self.lineEditEmail.text().strip()
        phonenum = self.lineEditPhoneNum.text().strip()
        username = self.lineEditUsername.text().strip()
        password = self.lineEditPassword.text().strip()
        confirm_password = self.lineEditConfirmPassword.text().strip()

        # Check if user agreed to T&C
        if not self.checkBoxAgreeTerm.isChecked():
            QMessageBox.warning(self.MainWindow, "Registration Error", "You must agree to the Terms and Conditions.")
            return

        # Check mandatory fields
        if not (name and email and phonenum and username and password and confirm_password):
            QMessageBox.warning(self.MainWindow, "Registration Error", "Please fill in all required fields.")
            return

        # Validate password match
        if password != confirm_password:
            QMessageBox.warning(self.MainWindow, "Registration Error", "Passwords do not match.")
            return

        # Validate email format
        if not is_valid_email(email):
            QMessageBox.warning(self.MainWindow, "Registration Error", "Invalid email format.")
            return

        # Check if email is already used
        for usr in self.users:
            if usr.Email.strip().lower() == email.lower():
                QMessageBox.warning(self.MainWindow, "Registration Error", "This email is already registered.")
                return

        # Validate phone format
        if not is_valid_phone(phonenum):
            QMessageBox.warning(self.MainWindow, "Registration Error", "Invalid phone number format. Digits only, 9-15 length.")
            return

        # Check if phone is already used
        for usr in self.users:
            if usr.PhoneNum == phonenum:
                QMessageBox.warning(self.MainWindow, "Registration Error", "This phone number is already registered.")
                return

        # Check if username is taken
        if self.dc.get_user_by_username(username):
            QMessageBox.warning(self.MainWindow, "Registration Error", "Username already exists. Please choose another.")
            return

        # Everything is valid, create the user
        new_user = User(
            Name=name,
            Email=email,
            PhoneNum=phonenum,
            Username=username,
            Password=password,   # DataConnector.add_user will hash it
            Avatar=self.avatar_path  # store the avatar path if any
        )

        self.dc.add_user(new_user)
        QMessageBox.information(self.MainWindow, "Success", "Account created successfully. Please log in.")

        # Close register window
        self.MainWindow.close()

        # Open login window
        self.mainwindow = QMainWindow()
        self.myui = login_ext.LoginMainWindowExt()
        self.myui.setupUi(self.mainwindow)
        self.mainwindow.show()

    def TermAndCodition(self):
        self.mainwindow = QMainWindow()
        from ui.TermAndCoditionsWindow.TermAndCoditionsWindowExt import TermAndCoditionsWindowExt
        self.myui = TermAndCoditionsWindowExt()
        self.myui.setupUi(self.mainwindow)
        self.myui.showWindow()

    def BackToLogin(self):
        self.MainWindow.close()
        self.mainwindow = QMainWindow()
        self.myui = login_ext.LoginMainWindowExt()
        self.myui.setupUi(self.mainwindow)
        self.myui.showWindow()
