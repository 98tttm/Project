import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QCheckBox, QLabel, QComboBox, QSlider, QDialog, QListWidget, QMenu,
    QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from functools import partial

# Import DataConnector và Project
from libs.DataConnector import DataConnector
from Models.Project import Project

class EditAssignmentDialog(QDialog):
    def __init__(self, parent, row):
        super().__init__(parent)
        self.setWindowTitle("Edit Assignment")
        self.setGeometry(350, 350, 400, 300)
        self.parent = parent
        self.row = row

        self.layout = QVBoxLayout(self)

        # Danh sách người đảm nhận
        self.list_widget = QListWidget()
        self.layout.addWidget(QLabel("Current Assignees:"))
        self.layout.addWidget(self.list_widget)

        self.load_assignments()

        # Ô nhập để thêm người mới
        self.new_assignee_input = QLineEdit()
        self.new_assignee_input.setPlaceholderText("Enter name to add")
        self.layout.addWidget(self.new_assignee_input)

        # Nút thêm người
        self.add_btn = QPushButton("Add Assignee")
        self.add_btn.clicked.connect(self.add_assignee)
        self.layout.addWidget(self.add_btn)

        # Kết nối sự kiện xóa khi nhấp chuột phải
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

    def load_assignments(self):
        self.list_widget.clear()
        for member in self.parent.projects[self.row].assignment:
            self.list_widget.addItem(member)

    def add_assignee(self):
        new_assignee = self.new_assignee_input.text().strip()
        if new_assignee:
            self.parent.projects[self.row].assignment.append(new_assignee)
            self.load_assignments()
            self.new_assignee_input.clear()
            self.update_main_table()

    def remove_assignee(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            name = selected_item.text()
            self.parent.projects[self.row].assignment.remove(name)
            self.load_assignments()
            self.update_main_table()

    def show_context_menu(self, position):
        menu = QMenu(self)
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(self.remove_assignee)
        menu.addAction(remove_action)
        menu.exec(self.list_widget.mapToGlobal(position))

    def update_main_table(self):
        assignment_btn = self.parent.table.cellWidget(self.row, 3)
        if self.parent.projects[self.row].assignment:
            assignment_btn.setText(", ".join(self.parent.projects[self.row].assignment))
        else:
            assignment_btn.setText("Edit")

class AddProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Project")
        self.setGeometry(300, 300, 400, 300)

        self.parent = parent  # để có thể cập nhật bảng
        self.layout = QVBoxLayout(self)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Project ID")
        self.layout.addWidget(QLabel("Project ID:"))
        self.layout.addWidget(self.id_input)

        self.name_input = QLineEdit()
        self.layout.addWidget(QLabel("Project Name:"))
        self.layout.addWidget(self.name_input)

        self.manager_input = QLineEdit()
        self.layout.addWidget(QLabel("Manager:"))
        self.layout.addWidget(self.manager_input)

        self.status_input = QComboBox()
        self.status_input.addItems(["Open", "Pending", "Ongoing", "Completed", "Canceled"])
        self.layout.addWidget(QLabel("Status:"))
        self.layout.addWidget(self.status_input)

        self.progress_input = QSlider(Qt.Orientation.Horizontal)
        self.progress_input.setRange(0, 100)
        self.layout.addWidget(QLabel("Progress:"))
        self.layout.addWidget(self.progress_input)

        self.start_date_input = QLineEdit()
        self.layout.addWidget(QLabel("Start Date:"))
        self.layout.addWidget(self.start_date_input)

        self.end_date_input = QLineEdit()
        self.layout.addWidget(QLabel("End Date:"))
        self.layout.addWidget(self.end_date_input)

        self.add_btn = QPushButton("Add Project")
        self.add_btn.clicked.connect(self.add_project)
        self.layout.addWidget(self.add_btn)

    def add_project(self):
        project = Project(
            project_id=self.id_input.text().strip(),
            name=self.name_input.text().strip(),
            assignment=[],  # Chưa có assignment
            manager=self.manager_input.text().strip(),
            status=self.status_input.currentText(),
            progress=self.progress_input.value(),
            start_date=self.start_date_input.text().strip(),
            end_date=self.end_date_input.text().strip()
        )

        if not project.project_id or not project.name:
            # Kiểm tra dữ liệu hợp lệ
            return

        if self.parent:  # Parent chính là ProjectManager
            self.parent.projects.append(project)
            # Hiển thị lại bảng
            self.parent.load_projects()
            # Lưu xuống file JSON
            self.parent.dc.save_all_projects(self.parent.projects)

        self.close()

class ProjectManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project List")
        self.setGeometry(100, 100, 1200, 600)

        self.dc = DataConnector()
        # Đọc danh sách Project từ JSON
        self.projects = self.dc.get_all_projects() or []

        self.layout = QVBoxLayout(self)

        # Ô tìm kiếm
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Project ID or Name")
        self.search_input.textChanged.connect(self.filter_projects)
        self.layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["Select", "ID", "Name", "Assignment", "Manager", "Status", "Progress", "Start Date", "End Date"])
        self.layout.addWidget(self.table)

        self.select_all_checkbox = QCheckBox("Select All Projects")
        self.select_all_checkbox.stateChanged.connect(self.select_all_projects)
        self.layout.addWidget(self.select_all_checkbox)

        self.add_btn = QPushButton("Add New Project")
        self.add_btn.clicked.connect(self.open_add_project_dialog)
        self.layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton("Remove Selected Projects")
        self.remove_btn.clicked.connect(self.remove_selected_projects)
        self.layout.addWidget(self.remove_btn)

        self.load_projects()

    def load_projects(self, filtered_projects=None):
        """Hiển thị (hoặc lọc) danh sách project ra bảng."""
        projects_to_display = filtered_projects if filtered_projects is not None else self.projects
        self.table.setRowCount(len(projects_to_display))

        for row, project in enumerate(projects_to_display):
            # Cột 0: Checkbox
            select_checkbox = QCheckBox()
            self.table.setCellWidget(row, 0, select_checkbox)

            # Cột 1: ID
            self.table.setItem(row, 1, QTableWidgetItem(project.project_id))
            # Cột 2: Name
            self.table.setItem(row, 2, QTableWidgetItem(project.name))

            # Cột 3: Assignment (nút Edit)
            assignment_btn = QPushButton(", ".join(project.assignment) if project.assignment else "Edit")
            assignment_btn.clicked.connect(partial(self.edit_assignment, row))
            self.table.setCellWidget(row, 3, assignment_btn)

            # Cột 4: Manager
            self.table.setItem(row, 4, QTableWidgetItem(project.manager))

            # Cột 5: Status (ComboBox)
            status_combo = QComboBox()
            status_combo.addItems(["Open", "Pending", "Ongoing", "Completed", "Canceled"])
            status_combo.setCurrentText(project.status)
            status_combo.currentTextChanged.connect(partial(self.update_status, row))
            self.table.setCellWidget(row, 5, status_combo)

            # Cột 6: Progress (Slider + Label)
            progress_layout = QHBoxLayout()
            progress_slider = QSlider(Qt.Orientation.Horizontal)
            progress_slider.setRange(0, 100)
            progress_slider.setValue(project.progress)

            progress_label = QLabel(f"{project.progress}%")
            progress_slider.valueChanged.connect(lambda value, r=row, label=progress_label: self.update_progress(r, value, label))

            progress_layout.addWidget(progress_slider)
            progress_layout.addWidget(progress_label)
            progress_widget = QWidget()
            progress_widget.setLayout(progress_layout)
            self.table.setCellWidget(row, 6, progress_widget)

            # Cột 7: Start Date
            self.table.setItem(row, 7, QTableWidgetItem(project.start_date))
            # Cột 8: End Date
            self.table.setItem(row, 8, QTableWidgetItem(project.end_date))

    def filter_projects(self):
        """Lọc dự án theo ID hoặc tên"""
        query = self.search_input.text().strip().lower()
        if not query:
            self.load_projects()
            return
        filtered_projects = [p for p in self.projects if query in p.project_id.lower() or query in p.name.lower()]
        self.load_projects(filtered_projects)

    def remove_selected_projects(self):
        """Xóa các dự án được chọn"""
        selected_rows = []
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                selected_rows.append(row)

        for row in reversed(selected_rows):
            del self.projects[row]

        self.load_projects()
        # Lưu thay đổi vào file JSON sau khi xóa
        self.dc.save_all_projects(self.projects)

    def update_status(self, row, value):
        """Cập nhật status cho project"""
        self.projects[row].status = value
        self.dc.save_all_projects(self.projects)

    def update_progress(self, row, value, label):
        """Cập nhật progress cho project"""
        self.projects[row].progress = value
        label.setText(f"{value}%")
        self.dc.save_all_projects(self.projects)

    def edit_assignment(self, row):
        dialog = EditAssignmentDialog(self, row)
        dialog.exec()

    def select_all_projects(self, state):
        """Chọn/bỏ chọn tất cả checkbox"""
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(state == Qt.CheckState.Checked.value)

    def open_add_project_dialog(self):
        """Mở dialog thêm project"""
        dialog = AddProjectDialog(self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProjectManager()
    window.show()
    sys.exit(app.exec())
