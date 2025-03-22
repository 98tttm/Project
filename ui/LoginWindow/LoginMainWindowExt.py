from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets

from libs.DataConnector import DataConnector
from ui.LoginWindow.LoginMainWindow import Ui_MainWindow
from ui.MainWindowNew.MainWindowNewExt import MainWindowNewExt
from ui.RegisterWindow.RegisterMainWindowExt import RegisterMainWindowExt

class LoginMainWindowExt(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.failed_attempts = 0
        self.max_attempts = 3
        self.password_hidden = True  # Start with hidden password

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.setupSignalAndSlot()

        # Start with password echo mode as "Password"
        self.lineEditPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEditUsername.setFocus()

    def showWindow(self):
        self.MainWindow.show()

    def setupSignalAndSlot(self):
        self.pushButtonLogin.clicked.connect(self.process_login)
        self.pushButtonForgot.clicked.connect(self.resetpasswordwindow)
        self.pushButtonRegister.clicked.connect(self.register)
        self.pushButtonHide.clicked.connect(self.toggle_password_visibility)
        self.pushButtonTerm.clicked.connect(self.term)
        self.pushButtonPrivacy.clicked.connect(self.privacy)

    def resetpasswordwindow(self):
        """Open 'Forgot Password' window."""
        from ui.ForgotPassWindow.ForgotPasswordWindowExt import ForgotPasswordWindowExt
        self.MainWindow.close()
        self.mainwindow = QMainWindow()
        self.myui = ForgotPasswordWindowExt()
        self.myui.setupUi(self.mainwindow)
        self.myui.showWindow()

    def register(self):
        """Open 'Register' window."""
        self.MainWindow.close()
        self.mainwindow = QMainWindow()
        self.myui = RegisterMainWindowExt()
        self.myui.setupUi(self.mainwindow)
        self.myui.showWindow()

    def process_login(self):
        dc = DataConnector()
        uid = self.lineEditUsername.text().strip()
        pwd = self.lineEditPassword.text().strip()

        # Basic validation: no empty fields
        if not uid or not pwd:
            QMessageBox.warning(self.MainWindow, "Thiếu thông tin", "Vui lòng điền đầy đủ tài khoản và mật khẩu.")
            return

        # If we have too many failed attempts, disallow
        if self.failed_attempts >= self.max_attempts:
            QMessageBox.critical(self.MainWindow, "Quá số lần cho phép",
                                 "Bạn đã nhập sai quá nhiều lần. Hãy thử lại sau.")
            self.MainWindow.close()
            return

        user = dc.login(uid, pwd)
        if user is not None:
            QMessageBox.information(self.MainWindow, "Chào mừng",
                                    f"Chào mừng {user.Name} đã đăng nhập thành công!")
            # Pass the authenticated user to MainWindowNewExt
            self.MainWindow.close()
            self.mainwindow = QMainWindow()
            self.myui = MainWindowNewExt(self.mainwindow, current_user=user)
            self.myui.showWindow()
        else:
            self.failed_attempts += 1
            remaining = self.max_attempts - self.failed_attempts
            QMessageBox.warning(self.MainWindow, "Lỗi đăng nhập",
                                f"Đăng nhập thất bại.\n"
                                f"Kiểm tra lại thông tin. (Còn {remaining} lần thử)")

    def toggle_password_visibility(self):
        """Toggle password echo mode in lineEditPassword."""
        if self.password_hidden:
            # Show password
            self.lineEditPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        else:
            # Hide password
            self.lineEditPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.password_hidden = not self.password_hidden

    def term(self):
        from ui.TermAndCoditionsWindow.TermAndCoditionsWindowExt import TermAndCoditionsWindowExt
        self.mainwindow = QMainWindow()
        self.myui = TermAndCoditionsWindowExt()
        self.myui.setupUi(self.mainwindow)
        self.myui.showWindow()

    def privacy(self):
        from ui.Privacy.PrivacyWindowExt import PrivacyWindowExt
        self.mainwindow = QMainWindow()
        self.myui = PrivacyWindowExt()
        self.myui.setupUi(self.mainwindow)
        self.myui.showWindow()
