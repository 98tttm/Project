import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class CreateProfileWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create your profile")
        self.resize(800, 400)

        # Main layout is horizontal: left side for profile info, right side for image display
        main_layout = QHBoxLayout(self)

        # LEFT SIDE LAYOUT
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        # Top bar (step label at top right within the left side)
        top_bar_layout = QHBoxLayout()
        # Left spacer
        top_bar_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        # Step label
        self.label_step = QLabel("Step 1 of 2")
        self.label_step.setStyleSheet("font-size:14px; color:black;")
        top_bar_layout.addWidget(self.label_step, alignment=Qt.AlignmentFlag.AlignRight)
        left_layout.addLayout(top_bar_layout)

        # Big title layout
        self.label_title = QLabel("Create your profile")
        self.label_title.setStyleSheet("font-size:24px; font-weight:bold;")
        left_layout.addWidget(self.label_title, alignment=Qt.AlignmentFlag.AlignLeft)

        # Upload photo button
        self.btn_upload_photo = QPushButton("Upload your photo")
        self.btn_upload_photo.setStyleSheet("QPushButton {border: 1px solid #ccc; padding: 8px;}")
        self.btn_upload_photo.clicked.connect(self.upload_photo)
        left_layout.addWidget(self.btn_upload_photo, alignment=Qt.AlignmentFlag.AlignLeft)

        # Name input
        self.lineedit_name = QLineEdit()
        self.lineedit_name.setPlaceholderText("Your name:")
        # Limit to 255 characters
        self.lineedit_name.setMaxLength(255)
        self.lineedit_name.textChanged.connect(self.update_char_count)
        left_layout.addWidget(self.lineedit_name, alignment=Qt.AlignmentFlag.AlignLeft)

        # Character count label
        self.label_char_count = QLabel("0/255")
        self.label_char_count.setStyleSheet("color:gray;")
        left_layout.addWidget(self.label_char_count, alignment=Qt.AlignmentFlag.AlignLeft)

        # Continue button (styled in red)
        self.btn_continue = QPushButton("Continue")
        self.btn_continue.setStyleSheet(
            "QPushButton { background-color:#ff0000; color:white; padding:10px 20px; border:none; }"
            "QPushButton:hover { background-color:#cc0000; }"
        )
        self.btn_continue.clicked.connect(self.continue_clicked)
        left_layout.addWidget(self.btn_continue, alignment=Qt.AlignmentFlag.AlignLeft)

        # Add stretch to push content up
        left_layout.addStretch()

        # RIGHT SIDE LAYOUT: display the chosen image
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)

        # Label to display the image
        self.labelImage = QLabel("No image selected")
        self.labelImage.setStyleSheet("border: 1px dashed #ccc; background-color:#fafafa;")
        self.labelImage.setFixedSize(300, 300)
        self.labelImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.labelImage, alignment=Qt.AlignmentFlag.AlignTop)

        # You could add more widgets to right_layout if desired
        right_layout.addStretch()

    def upload_photo(self):
        """
        Opens a file dialog for the user to pick an image.
        Copies the chosen image to a known location (optional).
        Displays the image in the right-side label.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select an Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            # For demonstration, we just load and display the image
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale the pixmap to fit the label's size if needed
                scaled_pix = pixmap.scaled(
                    self.labelImage.width(),
                    self.labelImage.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.labelImage.setPixmap(scaled_pix)
                self.labelImage.setText("")  # Clear the "No image selected" text
                # Optionally copy the file to a known location:
                #   avatars_dir = "../Dataset/avatars"
                #   if not os.path.exists(avatars_dir):
                #       os.makedirs(avatars_dir)
                #   base_name = os.path.basename(file_path)
                #   new_path = os.path.join(avatars_dir, base_name)
                #   shutil.copy(file_path, new_path)
            else:
                QMessageBox.warning(self, "Error", "Could not load the selected image.")
        else:
            # User canceled the file dialog
            pass

    def update_char_count(self):
        text_length = len(self.lineedit_name.text())
        self.label_char_count.setText(f"{text_length}/255")

    def continue_clicked(self):
        """
        Handle the continue button click.
        Validate the name or proceed to the next step.
        """
        user_name = self.lineedit_name.text().strip()
        if not user_name:
            QMessageBox.warning(self, "Error", "Please enter your name before continuing.")
            return
        # Proceed to the next step
        QMessageBox.information(self, "Next step", f"Name: {user_name}\nContinue to next step...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CreateProfileWidget()
    window.show()
    sys.exit(app.exec())
