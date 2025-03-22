import os
from PyQt6.QtGui import QPixmap
from ui.InformationAssigneeWindow.AssigneeMainWindow import Ui_MainWindow
from Models.User import User

class AssigneeMainWindowExt(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.setupSignals()

    def showWindow(self):
        self.MainWindow.show()

    def setupSignals(self):
        self.pushButtonClose.clicked.connect(self.close)

    def close(self):
        self.MainWindow.close()

    def display_user_info(self, user_obj: User, default_avatar_path="resources/default_avatar.png"):
        """
        Populates the UI with the selected user's information.
        :param user_obj: The User instance whose data we want to display.
        :param default_avatar_path: Path to a default image if user_obj.Avatar is missing or invalid.
        """
        # 1) Full name
        self.lineEditFullName.setText(user_obj.Name)

        # 2) ID (or username)
        self.lineEditID.setText(user_obj.Username)

        # 3) Work email
        self.lineEditEmail.setText(user_obj.Email)

        # 4) Phone number
        self.lineEditPhone.setText(user_obj.PhoneNum)

        # 5) Avatar
        if user_obj.Avatar and os.path.isfile(user_obj.Avatar):
            pixmap = QPixmap(user_obj.Avatar)
        else:
            pixmap = QPixmap(default_avatar_path)

        self.label_5.setPixmap(pixmap)
        self.label_5.setScaledContents(True)
