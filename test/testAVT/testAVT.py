import sys
import os
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QGraphicsView, QGraphicsScene, QMessageBox,
    QLabel
)

class SquareImageCropWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Square Image Uploader")
        self.resize(800, 600)

        # Central widget + layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # GraphicsView/Scene to show the loaded image
        self.scene = QGraphicsScene(self)
        self.graphics_view = QGraphicsView(self.scene)
        self.main_layout.addWidget(self.graphics_view)

        # Info label
        self.info_label = QLabel("No image loaded.")
        self.main_layout.addWidget(self.info_label)

        # Buttons layout
        btn_layout = QHBoxLayout()
        self.main_layout.addLayout(btn_layout)

        self.btn_upload = QPushButton("Upload Image")
        self.btn_crop = QPushButton("Crop to Square")
        self.btn_save = QPushButton("Save Cropped Image")

        btn_layout.addWidget(self.btn_upload)
        btn_layout.addWidget(self.btn_crop)
        btn_layout.addWidget(self.btn_save)

        # Connect signals
        self.btn_upload.clicked.connect(self.upload_image)
        self.btn_crop.clicked.connect(self.crop_to_square)
        self.btn_save.clicked.connect(self.save_cropped_image)

        # Internal storage
        self.original_pixmap = None
        self.cropped_pixmap = None

    def upload_image(self):
        """Open file dialog, load image into QGraphicsScene."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select an image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not file_path:
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Error", "Failed to load the image.")
            return

        self.original_pixmap = pixmap
        self.cropped_pixmap = None  # reset cropped

        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(QRectF(pixmap.rect()))
        self.info_label.setText(f"Loaded: {os.path.basename(file_path)}")

    def crop_to_square(self):
        """
        Crops the loaded image to a square, preserving the largest square
        region from the center. Then updates the scene to show the cropped version.
        """
        if not self.original_pixmap:
            QMessageBox.warning(self, "No Image", "Please upload an image first.")
            return

        pixmap = self.original_pixmap
        w = pixmap.width()
        h = pixmap.height()

        # Determine the size of the square: the smaller of width or height
        side = min(w, h)

        # Calculate top-left corner to center-crop
        x = (w - side) // 2
        y = (h - side) // 2

        # Crop the image
        square = pixmap.copy(x, y, side, side)
        self.cropped_pixmap = square

        # Show the cropped version in the scene
        self.scene.clear()
        self.scene.addPixmap(square)
        self.scene.setSceneRect(QRectF(square.rect()))

        self.info_label.setText(f"Cropped to {side}x{side} square.")

    def save_cropped_image(self):
        """Save the cropped image to disk."""
        if not self.cropped_pixmap:
            QMessageBox.warning(self, "No Cropped Image", "Please crop the image first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save cropped image", "", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)"
        )
        if not file_path:
            return

        # Attempt to save
        success = self.cropped_pixmap.save(file_path)
        if success:
            QMessageBox.information(self, "Saved", f"Image saved to:\n{file_path}")
        else:
            QMessageBox.warning(self, "Error", "Failed to save the cropped image.")

def main():
    app = QApplication(sys.argv)
    window = SquareImageCropWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
