from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QLineEdit, QPushButton, QMenu, QMessageBox


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
