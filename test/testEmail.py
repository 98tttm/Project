from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox, QLineEdit, QPushButton, QVBoxLayout, QLabel
from OTP.otp_handler import generate_otp, send_otp_html_email

class ForgotPasswordWindowExt(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.otp_code = None  # Lưu OTP gửi đi
        self.user_email = None  # Email của người dùng

        self.setWindowTitle("Forgot Password")
        self.setGeometry(300, 300, 400, 200)

        self.layout = QVBoxLayout(self)

        self.labelInfo = QLabel("Nhập Email của bạn:")
        self.layout.addWidget(self.labelInfo)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.layout.addWidget(self.email_input)

        self.btnSendOTP = QPushButton("Gửi OTP")
        self.btnSendOTP.clicked.connect(self.send_otp)
        self.layout.addWidget(self.btnSendOTP)

        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Nhập mã OTP")
        self.layout.addWidget(self.otp_input)

        self.btnVerify = QPushButton("Xác nhận OTP")
        self.btnVerify.clicked.connect(self.verify_otp)
        self.layout.addWidget(self.btnVerify)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Nhập mật khẩu mới")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.new_password_input)

        self.btnReset = QPushButton("Đặt lại mật khẩu")
        self.btnReset.clicked.connect(self.reset_password)
        self.layout.addWidget(self.btnReset)

    def send_otp(self):
        self.user_email = self.email_input.text().strip()
        if not self.user_email:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập email!")
            return
        # Tạo mã OTP
        self.otp_code = generate_otp()
        # Gửi OTP qua Gmail
        if send_otp_html_email(self.user_email, self.otp_code):
            QMessageBox.information(self, "Thành công", "Mã OTP đã được gửi tới email của bạn.")
        else:
            QMessageBox.critical(self, "Lỗi", "Gửi OTP thất bại.")

    def verify_otp(self):
        entered_otp = self.otp_input.text().strip()
        if entered_otp == self.otp_code:
            QMessageBox.information(self, "Thành công", "OTP chính xác. Bạn có thể đặt lại mật khẩu.")
        else:
            QMessageBox.warning(self, "Lỗi", "OTP không chính xác.")

    def reset_password(self):
        new_password = self.new_password_input.text().strip()
        if not new_password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu mới!")
            return
        # Ở đây bạn cần cập nhật mật khẩu mới cho user trong file dữ liệu.
        # Ví dụ: gọi hàm trong DataConnector: dc.update_password(self.user_email, new_password)
        QMessageBox.information(self, "Thành công", "Mật khẩu đã được cập nhật!")
        self.close()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ForgotPasswordWindowExt()
    window.show()
    sys.exit(app.exec())
