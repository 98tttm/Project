import logging
import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QMessageBox, QFileDialog, QListWidgetItem
)
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QIcon, QPixmap

from libs.email_assignee import send_assignment_html_email
from ui.AddProjectWindow.AddProjectWindowNew import Ui_MainWindow
from libs.DataConnector import DataConnector
from Models.Project import Project
from ui.InformationAssigneeWindow.AssingeeMainWindowExt import AssigneeMainWindowExt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AddProjectWindowNewExt(Ui_MainWindow):
    """
    Extended class to handle adding a new project with support for multiple assignees.
    lineEditProjectID đã được bỏ; ta auto-generate project_id dạng PRJxxx.
    """
    def __init__(self, onProjectAdded=None, main_ext=None):
        super().__init__()
        self.MainWindow = None
        self.onProjectAdded = onProjectAdded
        self.main_ext = main_ext

        self.dc = DataConnector()
        self.users = self.dc.get_all_users()       # For populating assignees
        self.projects = self.dc.get_all_projects() # For populating dependency list

        self.selected_assignees = []  # Store selected assignee usernames
        self.more_expanded = False

        # Path to default avatar image (adjust path as needed)
        self.default_avatar = os.path.join("resources", "default_avatar.png")

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        # Hide detail panel initially
        self.detailWidget.setVisible(False)

        # Fill combo boxes
        self.load_assignees()
        self.load_dependencies()

        # Set default date/time
        self.dateTimeStartDate.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEndDate.setDateTime(QDateTime.currentDateTime())

        # Connect signals
        self.pushButtonAdd.clicked.connect(self.add_project)
        self.pushButtonClear.clicked.connect(self.clear_fields)
        self.pushButtonMore.clicked.connect(self.toggle_detail_widget)
        self.pushButtonFile.clicked.connect(self.browse_file)
        self.pushButtonInfor.clicked.connect(self.show_assignee_info)

        # Multi-assignee: add/remove from list
        self.pushButtonAddAssignee.clicked.connect(self.add_assignee_to_list)
        self.pushButtonRemoveAssignee.clicked.connect(self.remove_selected_assignee)

    def showWindow(self):
        self.MainWindow.show()

    # 1) Hàm tự sinh Project ID
    def generate_new_project_id(self) -> str:
        """
        Tìm Project ID có dạng PRJxxx cao nhất, rồi +1.
        Ví dụ: PRJ001, PRJ002,...
        """
        max_num = 0
        for p in self.projects:
            if p.project_id.startswith("PRJ"):
                suffix = p.project_id[3:].strip()  # cắt "PRJ"
                try:
                    num = int(suffix)
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        new_num = max_num + 1
        return f"PRJ{new_num:03d}"

    # 2) Load combobox assignees
    def load_assignees(self):
        self.comboBoxAssignee.clear()
        self.comboBoxAssignee.addItem("- Select user -", None)
        for user in self.users:
            if user.Avatar and os.path.exists(user.Avatar):
                icon = QIcon(user.Avatar)
            else:
                icon = QIcon(self.default_avatar)
            self.comboBoxAssignee.addItem(icon, user.Username, user)

    # 3) Load combobox dependency
    def load_dependencies(self):
        self.comboBoxDependency.clear()
        self.comboBoxDependency.addItem("None")  # Means no dependency
        for proj in self.projects:
            self.comboBoxDependency.addItem(proj.project_id)

    # 4) Multi-assignee logic
    def add_assignee_to_list(self):
        user_obj = self.comboBoxAssignee.currentData()
        if not user_obj:
            QMessageBox.warning(self.MainWindow, "No user", "Please select a valid user.")
            return

        if user_obj.Username in self.selected_assignees:
            QMessageBox.information(self.MainWindow, "Duplicate", f"'{user_obj.Username}' is already added.")
            return

        self.selected_assignees.append(user_obj.Username)

        # create item with icon
        if user_obj.Avatar and os.path.exists(user_obj.Avatar):
            icon = QIcon(user_obj.Avatar)
        else:
            icon = QIcon(self.default_avatar)
        item = QListWidgetItem(icon, user_obj.Username)
        self.listWidgetAssignees.addItem(item)

    def remove_selected_assignee(self):
        item = self.listWidgetAssignees.currentItem()
        if not item:
            return
        username = item.text()
        if username in self.selected_assignees:
            self.selected_assignees.remove(username)
        row = self.listWidgetAssignees.row(item)
        self.listWidgetAssignees.takeItem(row)

    # 5) add_project -> auto-generate ID, create Project
    def add_project(self):
        proj_name = self.lineEditProjectName.text().strip()
        manager = self.lineEditManager.text().strip()
        desc = self.lineEditProjectName_2.text().strip()  # "task description"
        status = self.comboBoxStatus.currentText()

        # Generate ID
        proj_id = self.generate_new_project_id()

        if not proj_name:
            QMessageBox.warning(self.MainWindow, "Warning", "Project name is required.")
            return

        start_str = self.dateTimeStartDate.dateTime().toString("dd/MM/yyyy")
        end_str = self.dateTimeEndDate.dateTime().toString("dd/MM/yyyy")

        # If comboBoxAssignee has 1 user selected, add them if not in list
        single_pick = self.comboBoxAssignee.currentText()
        if single_pick not in ["- Select user -", ""] and single_pick not in self.selected_assignees:
            self.selected_assignees.append(single_pick)

        # detailWidget fields
        priority_pick = self.comboBoxPriority.currentText() if hasattr(self, 'comboBoxPriority') else "Normal"
        gantt_checked = self.checkBox.isChecked() if hasattr(self, 'checkBox') else False
        kanban_checked = self.checkBox_2.isChecked() if hasattr(self, 'checkBox_2') else False
        dragdrop_checked = self.checkBox_3.isChecked() if hasattr(self, 'checkBox_3') else False
        estimated_time = self.lineEdit_2.text().strip() if hasattr(self, 'lineEdit_2') else ""

        dependency_pick = self.comboBoxDependency.currentText()
        if dependency_pick == "None":
            dependency_pick = ""

        file_path = self.pushButtonFile.text()
        if file_path == "Attach file here...":
            file_path = ""
        attachments_list = [file_path] if file_path else []

        # Create the new Project
        new_proj = Project(
            project_id=proj_id,
            name=proj_name,
            assignment=self.selected_assignees[:],
            manager=manager,
            status=status,
            progress=0,
            start_date=start_str,
            end_date=end_str,
            description=desc,
            priority=priority_pick,
            dependency=dependency_pick,
            estimated_time=estimated_time,
            view_gantt=gantt_checked,
            view_kanban=kanban_checked,
            drag_and_drop=dragdrop_checked,
            attachments=attachments_list
        )

        # Save
        self.dc.add_project(new_proj)

        # Send email to each user
        for username in self.selected_assignees:
            user_obj = self.dc.get_user_by_username(username)
            if user_obj and user_obj.Email:
                success = send_assignment_html_email(user_obj.Email, new_proj)
                if success:
                    logger.info(f"Email sent to {user_obj.Email}")
                else:
                    logger.error(f"Failed to send email to {user_obj.Email}")

        QMessageBox.information(self.MainWindow,
                                "Success",
                                f"Project '{proj_name}' (ID: {proj_id}) added successfully!")

        # Gửi thông báo lên tabNotification
        if self.main_ext:
            self.main_ext.add_notification("added", new_proj, None)

        # callback
        if callable(self.onProjectAdded):
            self.onProjectAdded(new_proj)

        self.MainWindow.close()

    def clear_fields(self):
        self.lineEditProjectName.clear()
        self.lineEditManager.clear()
        self.lineEditProjectName_2.clear()
        self.comboBoxStatus.setCurrentIndex(0)
        self.comboBoxAssignee.setCurrentIndex(0)
        self.dateTimeStartDate.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEndDate.setDateTime(QDateTime.currentDateTime())
        self.pushButtonFile.setText("Attach file here...")

        # detailWidget
        if hasattr(self, 'comboBoxPriority'):
            self.comboBoxPriority.setCurrentIndex(0)
        if hasattr(self, 'checkBox'):
            self.checkBox.setChecked(False)
        if hasattr(self, 'checkBox_2'):
            self.checkBox_2.setChecked(False)
        if hasattr(self, 'checkBox_3'):
            self.checkBox_3.setChecked(False)
        if hasattr(self, 'lineEdit_2'):
            self.lineEdit_2.clear()
        if hasattr(self, 'comboBoxDependency'):
            self.comboBoxDependency.setCurrentIndex(0)

        self.selected_assignees.clear()
        if hasattr(self, 'listWidgetAssignees'):
            self.listWidgetAssignees.clear()

    def toggle_detail_widget(self):
        self.more_expanded = not self.more_expanded
        self.detailWidget.setVisible(self.more_expanded)
        self.pushButtonMore.setText("View less" if self.more_expanded else "View more")

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self.MainWindow, "Select file", "", "All Files (*)")
        if file_path:
            self.pushButtonFile.setText(file_path)

    def show_assignee_info(self):
        selected_item = self.listWidgetAssignees.currentItem()
        if not selected_item:
            QMessageBox.warning(self.MainWindow, "No Selection", "Please select an assignee from the list.")
            return

        username = selected_item.text()
        user_obj = self.dc.get_user_by_username(username)
        if not user_obj:
            QMessageBox.warning(self.MainWindow, "Error", f"User '{username}' not found in the database.")
            return

        # show user info
        self.assigneeWindow = QMainWindow()
        self.assigneeUI = AssigneeMainWindowExt()
        self.assigneeUI.setupUi(self.assigneeWindow)
        self.assigneeUI.display_user_info(user_obj)
        self.assigneeWindow.show()

# Test standalone
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = QMainWindow()
    ui = AddProjectWindowNewExt()
    ui.setupUi(main_win)
    main_win.show()
    sys.exit(app.exec())
