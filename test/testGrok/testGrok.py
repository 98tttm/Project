import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog, QVBoxLayout,
                             QLabel, QListWidget, QLineEdit, QPushButton, QMenu,
                             QMessageBox, QPushButton)


# Giả lập lớp Project để lưu trữ thông tin assignment
class Project:
    def __init__(self, name):
        self.name = name
        self.assignment = ["Alice", "Bob"]  # Danh sách assignee mặc định


# Giả lập lớp DataController để xử lý lưu trữ
class DataController:
    def save_all_projects(self, projects):
        print("Saving projects:", [p.assignment for p in projects])


# Lớp MainWindow giả lập làm parent
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Manager")
        self.projects = [Project("Project 1")]
        self.dc = DataController()

        # Nút để mở dialog
        self.btn_open_dialog = QPushButton("Edit Assignments", self)
        self.btn_open_dialog.clicked.connect(self.open_edit_dialog)
        self.setCentralWidget(self.btn_open_dialog)

    def open_edit_dialog(self):
        dialog = EditAssignmentDialog(self, self.projects[0])
        dialog.exec()

    def update_ui(self):
        print("UI updated with assignments:", self.projects[0].assignment)


# Lớp EditAssignmentDialog từ code của bạn
class EditAssignmentDialog(QDialog):
    def __init__(self, parent_ext, project):
        super().__init__(parent_ext)
        self.parent_ext = parent_ext
        self.project = project
        self.setWindowTitle("Edit Assignment")

        self.layout = QVBoxLayout(self)
        self.label = QLabel("Current Assignees:")
        self.layout.addWidget(self.label)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        # Right-click menu
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

        # Input for new assignee
        self.input_assignee = QLineEdit()
        self.input_assignee.setPlaceholderText("Enter new assignee name...")
        self.btn_add = QPushButton("Add Assignee")
        self.btn_add.clicked.connect(self.add_assignee)
        self.layout.addWidget(self.input_assignee)
        self.layout.addWidget(self.btn_add)

        self.load_assignees()

    def load_assignees(self):
        self.list_widget.clear()
        for name in self.project.assignment:
            self.list_widget.addItem(name)

    def add_assignee(self):
        name = self.input_assignee.text().strip()
        if not name:
            return
        if name in self.project.assignment:
            QMessageBox.warning(self, "Warning", f"{name} is already assigned.")
            return

        self.project.assignment.append(name)
        self.input_assignee.clear()
        self.load_assignees()
        self.save_changes()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        remove_act = QAction("Remove", self)
        remove_act.triggered.connect(self.remove_assignee)
        menu.addAction(remove_act)
        menu.exec(self.list_widget.mapToGlobal(pos))

    def remove_assignee(self):
        item = self.list_widget.currentItem()
        if item:
            name = item.text()
            if name in self.project.assignment:
                self.project.assignment.remove(name)
                self.load_assignees()
                self.save_changes()

    def save_changes(self):
        # Save to file
        self.parent_ext.dc.save_all_projects(self.parent_ext.projects)
        self.parent_ext.update_ui()


# Chạy ứng dụng
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())