import os
from PyQt6.QtGui import QPixmap

class User:
    def __init__(self, Name, Email, PhoneNum, Username, Password, Avatar=None):
        self.Name = Name
        self.Email = Email
        self.PhoneNum = PhoneNum
        self.Username = Username
        self.Password = Password
        # If no avatar is provided, use a default image (adjust the path as needed)
        self.Avatar = Avatar if Avatar else "D:\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\Image\avt.png"

    def get_avatar_pixmap(self):
        """
        Returns a QPixmap loaded from the avatar file.
        If the avatar file does not exist, it returns a QPixmap loaded from the default avatar.
        """
        if os.path.exists(self.Avatar):
            return QPixmap(self.Avatar)
        else:
            # Fallback to a default image (ensure default_avatar.png exists)
            return QPixmap("default_avatar.png")

    def __str__(self):
        return (
            f"{self.Name}\t{self.Email}\t{self.PhoneNum}\t"
            f"{self.Username}\t{self.Password}\t{self.Avatar}"
        )
