from PyQt6.QtWidgets import QMessageBox, QMainWindow
from PyQt6.QtWidgets import QLineEdit
from ui.ForgotPassWindow.ForgotPasswordWindow import Ui_MainWindow
from OTP.otp_handler import generate_otp, send_otp_html_email
from libs.DataConnector import DataConnector


class ForgotPasswordWindowExt(Ui_MainWindow):
    def setupUi(self, MainWindow):
        """
        Sets up the UI for a QMainWindow-based interface.
        'MainWindow' should be an instance of QMainWindow.
        """
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.setupSignalAndSlot()
        self.user_email = None
        self.otp_code = None
        self.dc = DataConnector()

        # Trạng thái hiện/ẩn mật khẩu
        self.new_password_visible = False
        self.confirm_password_visible = False

    def showWindow(self):
        """
        Show the QMainWindow in a non-modal way.
        """
        self.MainWindow.show()

    def setupSignalAndSlot(self):
        # Kết nối các nút với chức năng
        self.pushButtonSendOTP.clicked.connect(self.send_otp)
        self.pushButtonVerifyOTP.clicked.connect(self.verify_otp)
        self.pushButtonResetPassword.clicked.connect(self.reset_password)
        self.pushButtonBackToLogin.clicked.connect(self.login)
        self.pushButtonHide.clicked.connect(self.toggle_new_password_visibility)
        self.pushButtonHide2.clicked.connect(self.toggle_confirm_password_visibility)

    def send_otp(self):
        self.user_email = self.lineEditEmail.text().strip()
        if not self.user_email:
            QMessageBox.warning(self.MainWindow, "Error", "Please enter your email!")
            return

        # Check if email exists in user database
        users = self.dc.get_all_users()
        email_found = any(user.Email.strip().lower() == self.user_email.lower() for user in users)
        if not email_found:
            QMessageBox.warning(self.MainWindow, "Error", "The entered email does not exist in our system.")
            return

        self.otp_code = generate_otp()
        if send_otp_html_email(self.user_email, self.otp_code):
            QMessageBox.information(self.MainWindow, "Success", "OTP has been sent to your email.")
        else:
            QMessageBox.critical(self.MainWindow, "Error", "Failed to send OTP. Please try again later.")

    def verify_otp(self):
        entered_otp = self.lineEditOTP.text().strip()
        if entered_otp == self.otp_code:
            QMessageBox.information(self.MainWindow, "Success", "OTP is correct. You can now reset your password.")
        else:
            QMessageBox.warning(self.MainWindow, "Error", "OTP is incorrect. Please try again.")

    def reset_password(self):
        from ui.LoginWindow.LoginMainWindowExt import LoginMainWindowExt

        if not self.otp_code:
            QMessageBox.warning(self.MainWindow, "Error",
                                "Please request and verify OTP before resetting your password!")
            return

        entered_otp = self.lineEditOTP.text().strip()
        if entered_otp != self.otp_code:
            QMessageBox.warning(self.MainWindow, "Error",
                                "You must enter the correct OTP before resetting your password!")
            return

        new_password = self.lineEditNewPassword.text().strip()
        confirm_password = self.lineEditConfirmPassword.text().strip()

        if not new_password:
            QMessageBox.warning(self.MainWindow, "Error", "Please enter a new password!")
            return

        if not confirm_password:
            QMessageBox.warning(self.MainWindow, "Error", "Please confirm your new password!")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self.MainWindow, "Error", "Passwords do not match. Please try again.")
            return

        # Update password using DataConnector's update_password method.
        if self.dc.update_password(self.user_email, new_password):
            QMessageBox.information(self.MainWindow, "Success", "Your password has been updated!")
        else:
            QMessageBox.critical(self.MainWindow, "Error",
                                 "Failed to update password. Please check your email and try again.")
        self.MainWindow.close()
        self.mainwindow = QMainWindow()
        self.myui = LoginMainWindowExt()
        self.myui.setupUi(self.mainwindow)
        self.myui.showWindow()

    def login(self):
        from ui.LoginWindow.LoginMainWindowExt import LoginMainWindowExt
        self.MainWindow.close()
        self.mainwindow = QMainWindow()
        self.myui = LoginMainWindowExt()
        self.myui.setupUi(self.mainwindow)
        self.myui.showWindow()

    def toggle_new_password_visibility(self):
        """
        Toggle the visibility of the new password field.
        """
        if self.new_password_visible:
            self.lineEditNewPassword.setEchoMode(QLineEdit.EchoMode.Password)
            self.pushButtonHide.setText("Hiện")
        else:
            self.lineEditNewPassword.setEchoMode(QLineEdit.EchoMode.Normal)
            self.pushButtonHide.setText("Ẩn")
        self.new_password_visible = not self.new_password_visible

    def toggle_confirm_password_visibility(self):
        """
        Toggle the visibility of the confirm password field.
        """
        if self.confirm_password_visible:
            self.lineEditConfirmPassword.setEchoMode(QLineEdit.EchoMode.Password)
            self.pushButtonHide2.setText("Hiện")
        else:
            self.lineEditConfirmPassword.setEchoMode(QLineEdit.EchoMode.Normal)
            self.pushButtonHide2.setText("Ẩn")
        self.confirm_password_visible = not self.confirm_password_visible
