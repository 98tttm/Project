# File: AddProjectApp.py
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QMessageBox, QFileDialog
)
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QIcon


# Các class cần thiết (Giả sử các module này đã tồn tại)
# Nếu bạn không có các module này, bạn sẽ cần tạo chúng

class Ui_MainWindow:
    """
    Đây là class giả định từ file được tạo bởi PyQt Designer
    Trong thực tế, file này sẽ được tạo bằng pyuic6 từ file .ui
    """

    def setupUi(self, MainWindow):
        # Giả định setup UI cơ bản
        MainWindow.setWindowTitle("Add New Project")
        MainWindow.resize(800, 600)

        # Các widget cần thiết sẽ được định nghĩa ở đây
        # Trong ứng dụng thực tế, chúng sẽ được tạo từ file .ui


class DataConnector:
    """
    Giả định class kết nối dữ liệu
    """

    def get_all_users(self):
        # Giả định danh sách người dùng
        class User:
            def __init__(self, username, email, fullname):
                self.Username = username
                self.Email = email
                self.FullName = fullname

        return [
            User("user1", "user1@example.com", "User One"),
            User("user2", "user2@example.com", "User Two")
        ]

    def get_all_projects(self):
        # Giả định danh sách dự án
        class ProjectData:
            def __init__(self, id):
                self.project_id = id

        return [
            ProjectData("PROJ-001"),
            ProjectData("PROJ-002")
        ]

    def get_user_by_username(self, username):
        # Tìm người dùng theo username
        for user in self.get_all_users():
            if user.Username == username:
                return user
        return None

    def add_projects(self, project):
        # Giả định thêm dự án vào cơ sở dữ liệu
        print(f"Adding project: {project.name} (ID: {project.project_id})")
        # Trong thực tế, bạn sẽ lưu vào database ở đây
        return True


class Project:
    """
    Mô hình dữ liệu Project
    """

    def __init__(self, project_id, name, assignment, manager, status, progress, start_date, end_date):
        self.project_id = project_id
        self.name = name
        self.assignment = assignment
        self.manager = manager
        self.status = status
        self.progress = progress
        self.start_date = start_date
        self.end_date = end_date


# Định nghĩa lớp AddProjectWindowNewExt như đã cung cấp
class AddProjectWindowNewExt(Ui_MainWindow):
    """
    Extended class to handle the logic of adding a new project,
    toggling detail info, browsing for files, and picking assignees.
    """

    def __init__(self, onProjectAdded=None):
        """
        :param onProjectAdded: A callback function to invoke after a new project is successfully added.
        """
        super().__init__()
        self.MainWindow = None
        self.onProjectAdded = onProjectAdded
        self.dc = DataConnector()  # Access your data connector
        self.users = self.dc.get_all_users()  # We'll load these for comboBoxAssignee
        self.projects = self.dc.get_all_projects()  # For comboBoxDependency
        self.more_expanded = False  # Track if the detailWidget is visible

    def setupUi(self, MainWindow):
        """
        Standard UI setup plus signal wiring.
        """
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        # Giả định các widget này đã được tạo trong file .ui và có sẵn
        # Trong thực tế, bạn cần đảm bảo file .ui của bạn có các widget này
        self.lineEditProjectName = MainWindow.findChild(QLineEdit, "lineEditProjectName")
        self.lineEditProjectID = MainWindow.findChild(QLineEdit, "lineEditProjectID")
        self.lineEditManager = MainWindow.findChild(QLineEdit, "lineEditManager")
        self.lineEditProjectName_2 = MainWindow.findChild(QLineEdit, "lineEditProjectName_2")
        self.comboBoxStatus = MainWindow.findChild(QComboBox, "comboBoxStatus")
        self.comboBoxAssignee = MainWindow.findChild(QComboBox, "comboBoxAssignee")
        self.comboBoxDependency = MainWindow.findChild(QComboBox, "comboBoxDependency")
        self.dateTimeStartDate = MainWindow.findChild(QDateTimeEdit, "dateTimeStartDate")
        self.dateTimeEndDate = MainWindow.findChild(QDateTimeEdit, "dateTimeEndDate")
        self.pushButtonAdd = MainWindow.findChild(QPushButton, "pushButtonAdd")
        self.pushButtonClear = MainWindow.findChild(QPushButton, "pushButtonClear")
        self.pushButtonCancel = MainWindow.findChild(QPushButton, "pushButtonCancel")
        self.pushButtonMore = MainWindow.findChild(QPushButton, "pushButtonMore")
        self.pushButtonFile = MainWindow.findChild(QPushButton, "pushButtonFile")
        self.pushButtonInfor = MainWindow.findChild(QPushButton, "pushButtonInfor")
        self.detailWidget = MainWindow.findChild(QWidget, "detailWidget")

        # Initial states
        self.detailWidget.setVisible(False)  # Hide detail panel initially

        # Populate the assignee combo from user DB
        self.load_assignees()
        # Populate the dependency combo from existing project IDs
        self.load_dependencies()

        # Setup date/time fields
        self.dateTimeStartDate.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEndDate.setDateTime(QDateTime.currentDateTime())

        # Connect signals
        self.pushButtonAdd.clicked.connect(self.add_project)
        self.pushButtonClear.clicked.connect(self.clear_fields)
        self.pushButtonCancel.clicked.connect(self.close_window)
        self.pushButtonMore.clicked.connect(self.toggle_detail_widget)
        self.pushButtonFile.clicked.connect(self.browse_file)
        self.pushButtonInfor.clicked.connect(self.show_assignee_info)

    def showWindow(self):
        """
        Show the QMainWindow containing this UI.
        """
        self.MainWindow.show()

    # ----------------------
    # LOADERS
    # ----------------------
    def load_assignees(self):
        """
        Load all user usernames into comboBoxAssignee.
        """
        self.comboBoxAssignee.clear()
        self.comboBoxAssignee.addItem("- Selections -")
        for user in self.users:
            self.comboBoxAssignee.addItem(user.Username)

    def load_dependencies(self):
        """
        Load existing project IDs into comboBoxDependency.
        """
        self.comboBoxDependency.clear()
        self.comboBoxDependency.addItem("None")  # Means no dependency
        for proj in self.projects:
            self.comboBoxDependency.addItem(proj.project_id)

    # ----------------------
    # BUTTON HANDLERS
    # ----------------------
    def add_project(self):
        """
        Gather all input fields, create a new Project, save to data, and close.
        """
        proj_name = self.lineEditProjectName.text().strip()
        proj_id = self.lineEditProjectID.text().strip()
        manager = self.lineEditManager.text().strip()
        desc = self.lineEditProjectName_2.text().strip()  # The "task description"
        status = self.comboBoxStatus.currentText()

        if not proj_name or not proj_id:
            QMessageBox.warning(self.MainWindow, "Warning", "Project name and ID are required.")
            return

        # Start/end date in dd/MM/yyyy (or your chosen format)
        start_str = self.dateTimeStartDate.dateTime().toString("dd/MM/yyyy")
        end_str = self.dateTimeEndDate.dateTime().toString("dd/MM/yyyy")

        # Single assignee from combo (for demonstration)
        assignee = []
        selected_user = self.comboBoxAssignee.currentText()
        if selected_user not in ["- Selections -", ""]:
            assignee.append(selected_user)

        # Default progress = 0 (or from detailWidget if you like)
        new_proj = Project(
            project_id=proj_id,
            name=proj_name,
            assignment=assignee,
            manager=manager,
            status=status,
            progress=0,
            start_date=start_str,
            end_date=end_str,
        )

        # Save to data
        self.dc.add_projects(new_proj)

        QMessageBox.information(self.MainWindow, "Success", f"Project '{proj_name}' added successfully!")
        # If there's a callback for after project is added
        if self.onProjectAdded:
            self.onProjectAdded()
        self.MainWindow.close()

    def clear_fields(self):
        """
        Clear all input fields.
        """
        self.lineEditProjectName.clear()
        self.lineEditProjectID.clear()
        self.lineEditManager.clear()
        self.lineEditProjectName_2.clear()
        self.comboBoxStatus.setCurrentIndex(0)
        self.comboBoxAssignee.setCurrentIndex(0)
        self.dateTimeStartDate.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEndDate.setDateTime(QDateTime.currentDateTime())
        self.pushButtonFile.setText("Attach file here...")

    def close_window(self):
        """
        Close the add project window.
        """
        self.MainWindow.close()

    def toggle_detail_widget(self):
        """
        Show/hide the detailWidget panel. Change button text/icon accordingly.
        """
        self.more_expanded = not self.more_expanded
        self.detailWidget.setVisible(self.more_expanded)
        if self.more_expanded:
            self.pushButtonMore.setText("View less")
            # Optionally change icon to an "up arrow"
            # self.pushButtonMore.setIcon(QIcon("path/to/up_arrow.png"))
        else:
            self.pushButtonMore.setText("View more")
            # Optionally change icon to a "down arrow"
            # self.pushButtonMore.setIcon(QIcon("path/to/down_arrow.png"))

    def browse_file(self):
        """
        Let user pick a file from the system, store the path in pushButtonFile's text.
        """
        file_path, _ = QFileDialog.getOpenFileName(self.MainWindow, "Select file", "", "All Files (*)")
        if file_path:
            self.pushButtonFile.setText(file_path)

    def show_assignee_info(self):
        """
        Show a small info popup about the selected user from comboBoxAssignee.
        """
        username = self.comboBoxAssignee.currentText()
        if username in ["- Selections -", ""]:
            QMessageBox.warning(self.MainWindow, "No Selection", "No assignee selected.")
            return

        user_obj = self.dc.get_user_by_username(username)
        if not user_obj:
            QMessageBox.warning(self.MainWindow, "Error", f"User '{username}' not found in database.")
            return

        info_str = (
            f"Username: {user_obj.Username}\n"
            f"Email: {user_obj.Email}\n"
            f"FullName: {getattr(user_obj, 'FullName', 'N/A')}\n"
            # Add more fields if your User model has them
        )
        QMessageBox.information(self.MainWindow, "Assignee Info", info_str)


# Class cho cửa sổ chính
class AddProjectWindow(QMainWindow):
    def __init__(self, onProjectAdded=None):
        super().__init__()
        # Tạo UI và thiết lập
        self.ui = AddProjectWindowNewExt(onProjectAdded)
        self.ui.setupUi(self)


# Main function để chạy ứng dụng
def main():
    app = QApplication(sys.argv)

    # Callback function khi một dự án được thêm
    def on_project_added():
        print("Project added successfully!")

    # Tạo và hiển thị cửa sổ
    window = AddProjectWindow(on_project_added)
    window.show()

    # Chạy vòng lặp sự kiện
    sys.exit(app.exec())


# Chạy chương trình nếu file này được chạy trực tiếp
if __name__ == "__main__":
    # Thêm các import cần thiết cho setupUi
    from PyQt6.QtWidgets import (
        QLineEdit, QComboBox, QDateTimeEdit, QPushButton,
        QWidget, QMainWindow
    )

    main()