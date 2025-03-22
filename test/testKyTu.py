import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPlainTextEdit, QLabel
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt


def count_non_space_characters(text):
    """Return the number of characters in the text excluding spaces."""
    return len(text.replace(" ", ""))


class TextCounterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Counter")
        self.resize(400, 300)

        # Main layout
        layout = QVBoxLayout(self)

        # Plain text editor for user input
        self.text_edit = QPlainTextEdit(self)
        self.text_edit.textChanged.connect(self.update_count)
        layout.addWidget(self.text_edit)

        # Label to display character count (aligned to the bottom right)
        self.count_label = QLabel("Characters (no spaces): 0", self)
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.count_label)

    def update_count(self):
        text = self.text_edit.toPlainText()
        # Giới hạn tổng số ký tự là 255 (bao gồm cả khoảng trắng)
        if len(text) > 255:
            # Lưu vị trí con trỏ hiện tại
            cursor = self.text_edit.textCursor()
            pos = cursor.position()
            # Cắt bớt nội dung vượt quá 255 ký tự
            text = text[:255]
            # Ngăn chặn tín hiệu tái kích hoạt textChanged
            self.text_edit.blockSignals(True)
            self.text_edit.setPlainText(text)
            # Đưa con trỏ về vị trí cũ (hoặc vị trí cuối nếu vị trí cũ vượt quá 255)
            cursor.setPosition(min(pos, 255))
            self.text_edit.setTextCursor(cursor)
            self.text_edit.blockSignals(False)

        count = count_non_space_characters(text)
        self.count_label.setText(f"Characters (no spaces): {count}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextCounterWidget()
    window.show()
    sys.exit(app.exec())
