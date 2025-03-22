"""Lỗi - Rejected File"""
import sys
import logging
from collections import Counter
from datetime import datetime, timedelta
import os

from PyQt6.QtCore import Qt, QDate, QSize, QTimer, QRect
from PyQt6.QtGui import (QFont, QPainter, QPixmap, QPen, QColor, QAction, QIcon)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSlider, QCheckBox,
    QTableWidgetItem, QMenu, QMessageBox, QListWidget, QListWidgetItem, QFrame,
    QInputDialog, QFileDialog, QScrollArea, QToolButton, QSystemTrayIcon, QCalendarWidget
)
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QLineSeries

from Models.Notification import Notification
# ---------------------------------------------------------------------
# 1) Import DataConnector, Models, and UI files
# ---------------------------------------------------------------------
from libs.DataConnector import DataConnector
from libs.MySQLConnector import MySQLConnector
from libs.email_utils import send_assignment_html_email
from Models.Project import Project
from Models.User import User
from ui.AddProjectWindow.AddProjectWindowNewExt import AddProjectWindowNewExt
from ui.MainWindowNew.MainWindow_new import Ui_MainWindow

# ---------------------------------------------------------------------
# 2) Dialogs for editing assignments
# ---------------------------------------------------------------------
class AddAssigneeWindow(QDialog):
    """Dialog để chọn user (theo email) và add vào project.assignment."""
    def __init__(self, edit_dialog, project):
        super().__init__(edit_dialog)
        self.edit_dialog = edit_dialog
        self.main_ext = edit_dialog.main_ext
        self.project = project

        self.dc = self.main_ext.dc
        self.all_users = self.dc.get_all_users()

        self.setWindowTitle("Add Assignee")
        layout = QVBoxLayout(self)

        lbl = QLabel("Select a user to assign (by email):")
        layout.addWidget(lbl)

        self.combo_users = QComboBox()
        assigned = set(self.project.assignment)
        for user_obj in self.all_users:
            # Chỉ add user có email và chưa được assign
            if user_obj.Username not in assigned and user_obj.Email:
                self.combo_users.addItem(
                    f"{user_obj.Email} ({user_obj.Username})",
                    user_obj
                )
        layout.addWidget(self.combo_users)

        btn_add = QPushButton("Add Assignee")
        btn_add.clicked.connect(self.on_add)
        layout.addWidget(btn_add)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

    def on_add(self):
        selected_user = self.combo_users.currentData()
        if not selected_user:
            return
        username = selected_user.Username
        if username in self.project.assignment:
            QMessageBox.warning(self, "Warning", f"'{username}' is already assigned.")
            return

        # Thêm vào assignment
        self.project.assignment.append(username)
        self.dc.save_all_projects(self.main_ext.projects)
        self.main_ext.update_ui()

        # Gửi email
        if selected_user.Email:
            success = send_assignment_html_email(selected_user.Email, self.project)
            if success:
                QMessageBox.information(self, "Email Sent",
                                        f"Đã gửi email thông báo cho '{selected_user.Email}' về dự án.")
            else:
                QMessageBox.warning(self, "Email Failed",
                                    f"Gửi email thất bại đến '{selected_user.Email}'.")

        QMessageBox.information(self, "Assigned", f"Assigned '{username}' to project.")
        self.close()


class EditAssignmentDialog(QDialog):
    """Dialog xem/xoá assignees và mở AddAssigneeWindow."""
    def __init__(self, main_ext, project):
        super().__init__(main_ext)
        self.main_ext = main_ext
        self.dc = self.main_ext.dc
        self.project = project

        self.setWindowTitle("Edit Assignment")
        layout = QVBoxLayout(self)

        lbl = QLabel("Current Assignees:")
        layout.addWidget(lbl)

        self.list_assignees = QListWidget()
        self.list_assignees.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_assignees.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_assignees)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Assignee")
        btn_add.clicked.connect(self.open_add_assignee_window)
        btn_layout.addWidget(btn_add)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.load_assignments()

    def load_assignments(self):
        self.list_assignees.clear()
        all_users = self.main_ext.dc.get_all_users()
        for username in self.project.assignment:
            user_obj = next((u for u in all_users if u.Username == username), None)
            display_text = username
            if user_obj and user_obj.Email:
                display_text += f" ({user_obj.Email})"
            self.list_assignees.addItem(display_text)

    def open_add_assignee_window(self):
        dlg = AddAssigneeWindow(self, self.project)
        dlg.exec()
        self.load_assignments()
        self.update_main_table()

    def remove_assignee(self):
        item = self.list_assignees.currentItem()
        if item:
            username = item.text().split(" (")[0]
            if username in self.project.assignment:
                self.project.assignment.remove(username)
                self.update_main_table()
                self.load_assignments()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        act_remove = QAction("Remove", self)
        act_remove.triggered.connect(self.remove_assignee)
        menu.addAction(act_remove)
        menu.exec(self.list_assignees.mapToGlobal(pos))

    def update_main_table(self):
        self.main_ext.dc.save_all_projects(self.main_ext.projects)
        self.main_ext.update_ui()


# ---------------------------------------------------------------------
# 3) KanbanColumn and ProjectItem
# ---------------------------------------------------------------------
class ProjectItem(QListWidgetItem):
    """Item đại diện cho 1 Project trong Kanban board."""
    def __init__(self, project):
        super().__init__(f"{project.name}\n[Status: {project.status}]")
        self.project = project
        self.setFont(QFont("Arial", 10))
        self.setSizeHint(QSize(200, 70))

    def update_text(self):
        self.setText(f"{self.project.name}\n[Status: {self.project.status}]")


class KanbanColumn(QListWidget):
    """Cột Kanban cho phép kéo thả ProjectItem."""
    def __init__(self, main_ext, status, update_callback):
        super().__init__()
        self.main_ext = main_ext
        self.status = status
        self.update_callback = update_callback

        color_map = {
            "Open":      "#E6F7FF",
            "Pending":   "#FFF7E6",
            "Ongoing":   "#F6FFE6",
            "Completed": "#F7F7F7",
            "Canceled":  "#FFE6E6"
        }
        bg_color = color_map.get(status, "#f9f9f9")

        self.setStyleSheet(f"""
           QListWidget {{
               background-color: {bg_color};
               border: none;
           }}
           QListWidget::item {{
               margin: 8px; 
               border: 1px solid #cccccc;
               border-radius: 8px; 
               padding: 8px; 
               background-color: #ffffff;
           }}
           QListWidget::item:selected {{
               background-color: #cceeff; 
               border: 2px solid #3399ff;
           }}
        """)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        source = event.source()
        if source is self:
            super().dropEvent(event)
        else:
            if not event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
                event.ignore()
                return
            if source and source.currentItem():
                source_item = source.currentItem()
                if isinstance(source_item, ProjectItem):
                    project = source_item.project
                    project.status = self.status
                    new_item = ProjectItem(project)
                    drop_index = self.indexAt(event.position().toPoint())
                    if drop_index.isValid():
                        self.insertItem(drop_index.row(), new_item)
                    else:
                        self.addItem(new_item)
                    source.takeItem(source.row(source_item))
                    self.update_callback()
                event.acceptProposedAction()


# ---------------------------------------------------------------------
# 4) ProjectDetailsDialog
# ---------------------------------------------------------------------
class ProjectDetailsDialog(QDialog):
    """Dialog hiển thị chi tiết 1 project."""
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Details")
        self.project = project
        layout = QVBoxLayout(self)

        details = [
            f"Project ID: {project.project_id}",
            f"Name: {project.name}",
            f"Assignment: {', '.join(project.assignment)}",
            f"Manager: {project.manager}",
            f"Status: {project.status}",
            f"Progress: {project.progress}%",
            f"Start Date: {project.start_date}",
            f"End Date: {project.end_date}",
            f"Priority: {project.priority}",
            f"Dependency: {project.dependency}",
            f"Description: {project.description}",
            f"Attachments: {', '.join(project.attachments)}",
        ]
        for d in details:
            lbl = QLabel(d)
            layout.addWidget(lbl)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)


# --- Đồng hồ ở góc trên Gantt ---
class ClockWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.label.setStyleSheet("""
            font-size: 14px;
            color: #333333;
            background-color: #F0F0F0;
            padding: 5px 15px;
            border-radius: 3px;
        """)
        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        now = datetime.now()
        self.label.setText(f"⏰ {now.strftime('%H:%M:%S - %d/%m/%Y')}")


# --- GanttChartView: vẽ Gantt, cột tên project, timeline cuộn ngang ---
#  TÁCH LÀM 2 WIDGET: GanttNamesView và GanttTimelineView
# -------------------------------------------------------
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtWidgets import QWidget


class ScheduleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schedule Tracker")
        self.resize(600, 500)

        # Dictionary để lưu sự kiện: key=date_str, value=list of events
        self.events = {}

        # Layout chính
        main_layout = QHBoxLayout(self)

        # Bên trái: Calendar
        left_layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.load_events_for_date)
        left_layout.addWidget(self.calendar)
        main_layout.addLayout(left_layout)

        # Bên phải: list sự kiện và nút
        right_layout = QVBoxLayout()
        self.label_selected_date = QLabel("Events for " + self.calendar.selectedDate().toString("yyyy-MM-dd"))
        right_layout.addWidget(self.label_selected_date, alignment=Qt.AlignmentFlag.AlignCenter)

        self.list_events = QListWidget()
        right_layout.addWidget(self.list_events)

        # Ô nhập event + nút Add
        add_layout = QHBoxLayout()
        self.lineedit_event = QLineEdit()
        self.lineedit_event.setPlaceholderText("Enter new event...")
        add_layout.addWidget(self.lineedit_event)

        self.btn_add_event = QPushButton("Add Event")
        self.btn_add_event.clicked.connect(self.add_event)
        add_layout.addWidget(self.btn_add_event)
        right_layout.addLayout(add_layout)

        # Nút Remove
        self.btn_remove_event = QPushButton("Remove Selected Event")
        self.btn_remove_event.clicked.connect(self.remove_event)
        right_layout.addWidget(self.btn_remove_event)

        # Thêm khoảng trống
        right_layout.addStretch()

        main_layout.addLayout(right_layout)

    def load_events_for_date(self):
        """Hiển thị các sự kiện của ngày đang chọn."""
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString("yyyy-MM-dd")
        self.label_selected_date.setText("Events for " + date_str)
        self.list_events.clear()

        if date_str in self.events:
            for event in self.events[date_str]:
                self.list_events.addItem(event)

    def add_event(self):
        """Thêm sự kiện vào ngày đã chọn."""
        event_text = self.lineedit_event.text().strip()
        if not event_text:
            QMessageBox.warning(self, "Error", "Please enter an event description!")
            return

        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString("yyyy-MM-dd")
        if date_str not in self.events:
            self.events[date_str] = []
        self.events[date_str].append(event_text)
        self.load_events_for_date()
        self.lineedit_event.clear()

    def remove_event(self):
        """Xoá sự kiện đang chọn."""
        selected_items = self.list_events.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select an event to remove!")
            return
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString("yyyy-MM-dd")
        for item in selected_items:
            self.events[date_str].remove(item.text())
        self.load_events_for_date()

class GanttNamesView(QWidget):
    """
    Vẽ danh sách tên project bên trái, có header 'Projects'.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects = []
        self.row_height = 36
        self.header_height = 40
        self.label_width = 650 # Bạn có thể chỉnh nhỏ/lớn hơn tuỳ ý

    def set_projects(self, projects):
        self.projects = projects[:]
        # Tính chiều cao tối thiểu để đủ hiển thị tất cả
        total_height = self.header_height + len(projects)*self.row_height +10
        self.setMinimumHeight(total_height)
        # Độ rộng cột tên
        self.setFixedWidth(self.label_width)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Nền
        painter.fillRect(self.rect(), QColor("#FFFFFF"))

        # Header
        header_rect = QRect(0, 0, self.label_width, self.header_height)
        painter.fillRect(header_rect, QColor("#F0F0F0"))
        painter.setPen(QPen(QColor("#666666"), 1))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(header_rect, Qt.AlignmentFlag.AlignCenter, "Projects")

        # Kẻ đường ngang dưới header
        painter.setPen(QPen(QColor("#CCCCCC"), 1))
        painter.drawLine(0, self.header_height, self.label_width, self.header_height)

        # Vẽ tên project
        painter.setFont(QFont("Arial", 10))
        for i, proj in enumerate(self.projects):
            top_y = self.header_height + i*self.row_height
            # Nền xen kẽ
            if i % 2 == 0:
                painter.fillRect(0, top_y, self.label_width, self.row_height, QColor("#FAFAFA"))
            else:
                painter.fillRect(0, top_y, self.label_width, self.row_height, QColor("#FFFFFF"))

            # Vẽ text
            text_rect = QRect(5, top_y, self.label_width - 10, self.row_height)
            painter.setPen(QPen(QColor("#333333"), 1))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, proj.name)

            # Kẻ đường mỏng chia row
            painter.setPen(QPen(QColor("#EEEEEE"), 1))
            painter.drawLine(0, top_y + self.row_height, self.label_width, top_y + self.row_height)

class GanttTimeLineView(QWidget):
    """
    Vẽ phần timeline (thanh progress, ngày tháng, v.v.)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects = []
        self.days_to_show = 365
        self.cell_width = 40
        self.row_height = 36
        self.header_height = 40
        self.label_width = 0 # phải trùng hoặc gần với GanttNamesView để canh cột

        self.start_date = None

    def set_projects(self, projects):
        self.projects = projects
        if projects:
            earliest = None
            for p in projects:
                dt = self._parse_date(p.start_date)
                if not earliest or dt < earliest:
                    earliest = dt
            self.start_date = earliest if earliest else datetime.now()
        else:
            self.start_date = datetime.now()

        # Tính chiều cao tối thiểu
        total_height = self.header_height + len(projects)*self.row_height + 20
        # Tính chiều rộng tối thiểu
        timeline_w = self.cell_width*self.days_to_show + 200
        self.setMinimumSize(timeline_w, total_height)
        self.update()

    def _parse_date(self, date_str):
        fmts = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
        for f in fmts:
            try:
                return datetime.strptime(date_str, f)
            except:
                pass
        return datetime.now()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Nền trắng
        painter.fillRect(self.rect(), QColor("#FFFFFF"))

        # Vẽ header timeline
        painter.fillRect(self.label_width, 0, w-self.label_width, self.header_height, QColor("#F9F9F9"))
        painter.setPen(QPen(QColor("#AAAAAA"), 1))
        painter.drawLine(self.label_width, self.header_height, w, self.header_height)

        # Chia header (tháng/năm + ngày)
        month_header_h = 20
        day_header_h   = self.header_height - month_header_h

        # Vẽ block tháng
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        segment_start_x = self.label_width
        segment_start_date = self.start_date
        current_month = segment_start_date.month

        for i in range(self.days_to_show+1):
            day_date = self.start_date + timedelta(days=i)
            if i == 0:
                segment_start_x = self.label_width
                segment_start_date = day_date
                current_month = day_date.month
            else:
                if day_date.month != current_month or i == self.days_to_show:
                    total_days = (day_date - segment_start_date).days
                    if i == self.days_to_show:
                        total_days += 1
                    segment_width = total_days * self.cell_width
                    month_name = segment_start_date.strftime("%B %Y")
                    painter.drawText(segment_start_x, 0, segment_width, month_header_h,
                                     Qt.AlignmentFlag.AlignCenter, month_name)
                    # Vạch dọc chia tháng
                    painter.setPen(QPen(QColor("#BBBBBB"), 1))
                    painter.drawLine(segment_start_x, 0, segment_start_x, h)

                    segment_start_x += segment_width
                    segment_start_date = day_date
                    current_month = day_date.month

        # Vẽ hàng ngày
        painter.setFont(QFont("Arial", 9))
        painter.setPen(QPen(QColor("#CCCCCC"), 1))
        for i in range(self.days_to_show):
            day_date = self.start_date + timedelta(days=i)
            x = self.label_width + i*self.cell_width

            # highlight hôm nay
            if day_date.date() == datetime.now().date():
                painter.fillRect(x, month_header_h, self.cell_width, day_header_h, QColor("#E6F7FF"))

            day_str = day_date.strftime("%d")
            painter.drawText(x, month_header_h, self.cell_width, day_header_h,
                             Qt.AlignmentFlag.AlignCenter, day_str)
            painter.drawLine(x, self.header_height, x, h)

        # Vẽ thanh progress cho mỗi project
        for idx, proj in enumerate(self.projects):
            top_y = self.header_height + idx*self.row_height
            start_dt = self._parse_date(proj.start_date)
            end_dt   = self._parse_date(proj.end_date)
            if end_dt < start_dt:
                end_dt = start_dt

            days_from_start = (start_dt - self.start_date).days
            dur = (end_dt - start_dt).days + 1
            if days_from_start < 0:
                dur += days_from_start
                days_from_start = 0

            task_x = self.label_width + days_from_start*self.cell_width
            task_width = dur*self.cell_width

            # Giới hạn vẽ trong timeline
            max_timeline_x = self.label_width + self.days_to_show*self.cell_width
            if task_x + task_width > max_timeline_x:
                task_width = max_timeline_x - task_x

            bar_rect = QRect(task_x, top_y+5, task_width, self.row_height-10)

            progress_val = getattr(proj, "progress", 0)
            progress_val = max(0, min(100, progress_val))
            progress_w = int(task_width*(progress_val/100.0))

            # phần progress (xanh)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#4ECDC4"))
            painter.drawRect(bar_rect.x(), bar_rect.y(), progress_w, bar_rect.height())

            # phần còn lại (xám)
            painter.setBrush(QColor("#DDDDDD"))
            painter.drawRect(bar_rect.x()+progress_w, bar_rect.y(),
                             bar_rect.width()-progress_w, bar_rect.height())

            # viền
            painter.setPen(QPen(QColor("#000000"), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(bar_rect)

            # text % ở giữa
            painter.drawText(bar_rect, Qt.AlignmentFlag.AlignCenter, f"{progress_val}%")

            # Kẻ line mỏng ngang
            painter.setPen(QPen(QColor("#EEEEEE"), 1))
            #painter.drawLine(self.label_width, top_y+self.row_height, w, top_y+self.row_height)

        # Đường đỏ chỉ thời gian hiện tại
        now = datetime.now()
        delta = (now - self.start_date).total_seconds()/(24*3600)
        time_x = self.label_width + delta*self.cell_width
        if self.label_width <= time_x <= w:
            painter.setPen(QPen(QColor("#FF0000"), 2))
            painter.drawLine(int(time_x), self.header_height, int(time_x), h)

class GanttContainer(QWidget):
    """
    Gồm 2 scroll area:
      - namesScroll (chứa GanttNamesView)
      - timelineScroll (chứa GanttTimeLineView)
    Đồng bộ cuộn dọc, để nhìn gọn gàng,
    và có thể scroll xem tất cả project.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.namesView = GanttNamesView()
        self.timelineView = GanttTimeLineView()

        # Scroll cho cột tên
        self.namesScroll = QScrollArea()
        self.namesScroll.setWidget(self.namesView)
        self.namesScroll.setWidgetResizable(False)
        # Cho cuộn dọc luôn, ẩn cuộn ngang
        self.namesScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.namesScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Bỏ khung
        self.namesScroll.setFrameShape(QFrame.Shape.NoFrame)

        # Scroll cho timeline
        self.timelineScroll = QScrollArea()
        self.timelineScroll.setWidget(self.timelineView)
        self.timelineScroll.setWidgetResizable(False)
        # Cho cuộn dọc + ngang
        self.timelineScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.timelineScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.timelineScroll.setFrameShape(QFrame.Shape.NoFrame)

        # Layout
        h_layout = QHBoxLayout(self)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)
        h_layout.addWidget(self.namesScroll)
        h_layout.addWidget(self.timelineScroll)

        # Đồng bộ thanh cuộn dọc
        self.namesScroll.verticalScrollBar().valueChanged.connect(self.sync_scroll_from_left)
        self.timelineScroll.verticalScrollBar().valueChanged.connect(self.sync_scroll_from_right)

    def sync_scroll_from_left(self, val):
        self.timelineScroll.verticalScrollBar().setValue(val)

    def sync_scroll_from_right(self, val):
        self.namesScroll.verticalScrollBar().setValue(val)

    def set_projects(self, projects):
        self.namesView.set_projects(projects)
        self.timelineView.set_projects(projects)
        # Đưa scrollbar về top
        self.namesScroll.verticalScrollBar().setValue(0)
        self.timelineScroll.verticalScrollBar().setValue(0)

class   MainWindowNewExt(QMainWindow, Ui_MainWindow):
    def __init__(self, main_window: QMainWindow, current_user: User = None):
        super().__init__()
        self.mysql = MySQLConnector(host="localhost", user="root", password="", database="procheck_db")
        self.MainWindow = main_window
        self.setupUi(self.MainWindow)

        self.dc = DataConnector()
        self.projects = self.dc.get_all_projects() or []
        self.users = self.dc.get_all_users() or []
        self.current_user = current_user

        self.notification_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Dataset", "notifications.json")
        self.notifications = []

        self.setup_tray_icon()

        # Setup UI
        self.setup_table()
        self.setup_charts()
        self.setup_signals()
        self.setup_kanban_board()
        self.setup_account_tab()
        self.setup_gantt_tab()

        #setup tab Open, Pending, Ongoing, Completed, Canceled
        self.setup_tab_open()
        self.setup_tab_pending()
        self.setup_tab_ongoing()
        self.setup_tab_completed()
        self.setup_tab_canceled()

        self.setup_notifications_tab()
        self.load_notifications()
        self.update_notifications_view()

        print("Notifications count =", len(self.notifications))

        # Load
        self.update_project_counts()
        self.show_projects()
        self.load_kanban_projects()
        self.update_account_display()

        self.setup_search_buttons()

    def showWindow(self):
        self.MainWindow.show()

    def setup_search_buttons(self):
        """Gắn sự kiện cho các nút Home, Today, Activity (trong tab Search)."""
        if hasattr(self, "pushButtonHome"):
            self.pushButtonHome.clicked.connect(self.go_home)
        if hasattr(self, "pushButtonToday"):
            self.pushButtonToday.clicked.connect(self.show_schedule)
        if hasattr(self, "pushButtonActivity"):
            self.pushButtonActivity.clicked.connect(self.show_activity)

    def go_home(self):
        """Nhảy về màn hình Dashboard (ví dụ: tab index 1 trong QTabWidget 'QWidget')."""
        # Tùy index tab của bạn – ở đây giả sử 0=tab_5, 1=tab (dashboard), 2=widget, ...
        self.QWidget.setCurrentIndex(1)

    def show_schedule(self):
        """Mở cửa sổ lịch + sự kiện."""
        self.schedule_widget = ScheduleWidget()
        self.schedule_widget.show()

    def show_activity(self):
        """Nhảy sang tab Notification (giả sử index=5)."""
        # Tùy theo thứ tự tab, bạn chỉnh index cho đúng
        self.QWidget.setCurrentIndex(5)

    #  Tạo hàm sinh Project ID tự động: "PRJ001", "PRJ002", ...
    # ---------------------------------------------------------------------
    def generate_new_project_id(self) -> str:
        max_num = 0
        for p in self.projects:
            if p.project_id.startswith("PRJ"):
                try:
                    num_part = p.project_id[3:]  # Bỏ "PRJ"
                    num_val = int(num_part)
                    if num_val > max_num:
                        max_num = num_val
                except:
                    pass
        new_num = max_num + 1
        return f"PRJ{new_num:03d}"

    # --- PHẦN THÔNG BÁO ---

    def create_notification_card(self, noti: Notification) -> QWidget:
        """Tạo một card (QWidget) hiển thị thông tin của một notification."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        # Lấy thông tin user
        user_obj = self.dc.get_user_by_username(noti.username)
        avatar = QLabel()
        avatar.setFixedSize(50, 50)
        if user_obj and user_obj.Avatar and os.path.exists(user_obj.Avatar):
            pix = QPixmap(user_obj.Avatar).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation)
        else:
            pix = QPixmap("/Image/avt.png").scaled(
                50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        avatar.setPixmap(pix)
        layout.addWidget(avatar)
        # Thông tin bên phải
        info_layout = QVBoxLayout()
        # Hiển thị tên user và thời gian
        user_name = user_obj.Name if user_obj else noti.username
        lbl_user = QLabel(f"<b>{user_name}</b> <small>({noti.time_str})</small>")
        info_layout.addWidget(lbl_user)
        # Lấy tên dự án
        proj_obj = self.dc.get_project_by_projectid(noti.project_id)
        proj_name = proj_obj.name if proj_obj else noti.project_id
        lbl_action = QLabel(f"<b><i>{noti.action.capitalize()}</i></b> project <b>{proj_name}</b>")
        info_layout.addWidget(lbl_action)
        # Nếu có, hiển thị trạng thái của dự án
        status = proj_obj.status if proj_obj else "N/A"
        lbl_status = QLabel(f"Status: <b>{status}</b>")
        info_layout.addWidget(lbl_status)
        layout.addLayout(info_layout)
        return card

    def setup_notifications_tab(self):
        """Thiết lập giao diện cho tab Notification sử dụng QScrollArea và QVBoxLayout."""
        if hasattr(self, "tabNotification"):
            # Nếu chưa có layout, tạo mới và đặt container cho notifications
            layout = QVBoxLayout()
            self.tabNotification.setLayout(layout)

            title = QLabel("Notifications:")
            title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            layout.addWidget(title)

            # Tạo container widget cho các card thông báo
            self.notificationContainer = QWidget()
            self.notificationLayout = QVBoxLayout(self.notificationContainer)
            self.notificationLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

            # Tạo QScrollArea để cuộn danh sách thông báo
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(self.notificationContainer)
            layout.addWidget(scroll)

    def add_notification(self, action: str, project: Project, user: User = None):
        """Thêm 1 notification vào self.notifications, lưu file JSON, và cập nhật hiển thị."""
        if user is None:
            user = self.current_user

        now_str = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

        new_noti = Notification(
            username=user.Username if user else "",
            action=action,
            project_id=project.project_id if project else "",
            time_str=now_str
        )

        self.notifications.append(new_noti)
        print(">>> After add_notification, total noti =", len(self.notifications))

        # Hiển thị popup system tray
        message_title = "New Notification"
        if project:
            message_body = f"{user.Name} {action} project '{project.project_id}'"
        else:
            message_body = f"{user.Name} {action} project"
        self.trayIcon.showMessage(
            message_title,
            message_body,
            QIcon("/Image/notification_8625350.png"),
            3000
        )

        # Chuyển danh sách notification sang list[dict]
        data_list = [{
            "username": noti.username,
            "action": noti.action,
            "project_id": noti.project_id,
            "time_str": noti.time_str
        } for noti in self.notifications]

        if self.dc.save_notifications(data_list):
            print("✅ Notifications saved successfully.")
        else:
            print("❌ Error saving notifications.")
            # Cập nhật giao diện hiển thị thông báo
        self.update_notifications_view()

    def load_notifications(self):
        """Đọc file notifications.json và xây dựng lại danh sách notifications."""
        data_list = self.dc.load_notifications()
        print("Loaded notifications from file:", data_list)
        self.notifications.clear()
        for d in data_list:
            n = Notification(
                username=d.get("username", ""),
                action=d.get("action", ""),
                project_id=d.get("project_id", ""),
                time_str=d.get("time_str", "")
            )
            self.notifications.append(n)

    def update_notifications_view(self):
        """
        Cập nhật giao diện hiển thị danh sách thông báo.
        Các thông báo được sắp xếp theo thứ tự mới nhất lên đầu.
        """
        if not hasattr(self, "notificationLayout"):
            return

        # Xoá hết các widget cũ trong notificationLayout
        while self.notificationLayout.count():
            child = self.notificationLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Thêm các card thông báo vào layout (thứ tự đảo ngược: mới nhất ở đầu)
        for noti in reversed(self.notifications):
            card = self.create_notification_card(noti)
            self.notificationLayout.addWidget(card)

        self.notificationContainer.adjustSize()
        self.tabNotification.update()

    def setup_tray_icon(self):
        """Khởi tạo QSystemTrayIcon để hiển thị popup notification góc màn hình."""
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon("/Image/notification_8625350.png"))
        self.trayIcon.setToolTip("Notifications")
        self.trayIcon.show()

    def setup_tab_open(self):
        if hasattr(self, "pushButtonOpenAddTask"):
            self.pushButtonOpenAddTask.clicked.connect(self.open_add_project_open)
        if hasattr(self, "pushButtonOpenDelete"):
            self.pushButtonOpenDelete.clicked.connect(self.remove_selected_projects_open)
        if hasattr(self, "pushButtonOpenSearch"):
            self.pushButtonOpenSearch.clicked.connect(self.filter_projects_open)
        if hasattr(self, "pushButtonOpenReload"):
            self.pushButtonOpenReload.clicked.connect(self.reset_filter_open)
        if hasattr(self, "checkBoxSelectAllOpen"):
            self.checkBoxSelectAllOpen.stateChanged.connect(self.select_all_projects_open)

        if hasattr(self, "tableWidgetOpen"):
            self.tableWidgetOpen.setColumnCount(14)
            self.tableWidgetOpen.setHorizontalHeaderLabels([
                "Select", "ID", "Name", "Assignment", "Manager",
                "Status", "Progress", "Start Date", "End Date",
                "Priority", "Dependency", "Description", "Attachments", "Details"
            ])
            self.tableWidgetOpen.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.tableWidgetOpen.customContextMenuRequested.connect(self.show_context_menu_open)
        self.show_projects_open()

    def show_projects_open(self):
        if not hasattr(self, "tableWidgetOpen"):
            return
        table = self.tableWidgetOpen
        table.setRowCount(0)
        open_projects = [p for p in self.projects if p.status == "Open"]
        for row, project in enumerate(open_projects):
            table.insertRow(row)
            cb = QCheckBox()
            table.setCellWidget(row, 0, cb)
            table.setItem(row, 1, QTableWidgetItem(project.project_id))
            table.setItem(row, 2, QTableWidgetItem(project.name))
            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project_open)
            table.setCellWidget(row, 3, btn_assign)
            table.setItem(row, 4, QTableWidgetItem(project.manager))
            combo = self.create_status_combo(project, refresh_fn=self.show_projects_open)
            table.setCellWidget(row, 5, combo)
            prog_widget = self.create_progress_widget(project, refresh_fn=self.show_projects_open)
            table.setCellWidget(row, 6, prog_widget)
            table.setItem(row, 7, QTableWidgetItem(project.start_date))
            table.setItem(row, 8, QTableWidgetItem(project.end_date))
            table.setItem(row, 9, QTableWidgetItem(project.priority))
            dep = project.dependency or ""
            table.setItem(row, 10, QTableWidgetItem(dep))
            table.setItem(row, 11, QTableWidgetItem(project.description))
            attach_str = ", ".join(project.attachments) if project.attachments else ""
            table.setItem(row, 12, QTableWidgetItem(attach_str))
            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details_open)
            table.setCellWidget(row, 13, btn_details)

    def open_add_project_open(self):
        self.mainwindow_open = QMainWindow()
        self.myui_open = AddProjectWindowNewExt(onProjectAdded=self.load_projects_open, main_ext=self)
        self.myui_open.setupUi(self.mainwindow_open)
        self.mainwindow_open.show()

    def load_projects_open(self, new_project=None):
        self.projects = self.dc.get_all_projects() or []
        self.show_projects_open()


    def remove_selected_projects_open(self):
        if not hasattr(self, "tableWidgetOpen"):
            return
        table = self.tableWidgetOpen
        selected_rows = []
        for row in range(table.rowCount()):
            w = table.cellWidget(row, 0)
            if isinstance(w, QCheckBox) and w.isChecked():
                selected_rows.append(row)
        open_projects = [p for p in self.projects if p.status == "Open"]
        for row in reversed(selected_rows):
            if row < len(open_projects):
                proj = open_projects[row]
                self.projects.remove(proj)
                self.add_notification("deleted", proj, self.current_user)
        self.dc.save_all_projects(self.projects)
        self.show_projects_open()

    def filter_projects_open(self):
        if not hasattr(self, "lineEditSearchOpen"):
            return
        query = self.lineEditSearchOpen.text().strip().lower()
        if not query:
            self.show_projects_open()
            return
        open_projects = [p for p in self.projects if p.status == "Open"]
        filtered = [p for p in open_projects if query in p.project_id.lower() or query in p.name.lower()]
        self.show_filtered_projects_open(filtered)

    def show_filtered_projects_open(self, projs):
        table = self.tableWidgetOpen
        table.setRowCount(0)
        for row, project in enumerate(projs):
            table.insertRow(row)
            cb = QCheckBox()
            table.setCellWidget(row, 0, cb)
            table.setItem(row, 1, QTableWidgetItem(project.project_id))
            table.setItem(row, 2, QTableWidgetItem(project.name))
            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project_open)
            table.setCellWidget(row, 3, btn_assign)
            table.setItem(row, 4, QTableWidgetItem(project.manager))
            combo = self.create_status_combo(project, refresh_fn=self.show_projects_open)
            table.setCellWidget(row, 5, combo)
            prog_widget = self.create_progress_widget(project, refresh_fn=self.show_projects_open)
            table.setCellWidget(row, 6, prog_widget)
            table.setItem(row, 7, QTableWidgetItem(project.start_date))
            table.setItem(row, 8, QTableWidgetItem(project.end_date))
            table.setItem(row, 9, QTableWidgetItem(project.priority))
            dep = project.dependency or ""
            table.setItem(row, 10, QTableWidgetItem(dep))
            table.setItem(row, 11, QTableWidgetItem(project.description))
            attach_str = ", ".join(project.attachments) if project.attachments else ""
            table.setItem(row, 12, QTableWidgetItem(attach_str))
            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details_open)
            table.setCellWidget(row, 13, btn_details)

    def reset_filter_open(self):
        if hasattr(self, "lineEditSearchOpen"):
            self.lineEditSearchOpen.clear()
        self.show_projects_open()

    def select_all_projects_open(self, state):
        if not hasattr(self, "tableWidgetOpen"):
            return
        table = self.tableWidgetOpen
        for row in range(table.rowCount()):
            w = table.cellWidget(row, 0)
            if isinstance(w, QCheckBox):
                w.setChecked(state == Qt.CheckState.Checked.value)

    def show_context_menu_open(self, pos):
        if not hasattr(self, "tableWidgetOpen"):
            return
        table = self.tableWidgetOpen
        menu = QMenu(self)
        act_edit = QAction("Edit Project", self)
        act_delete = QAction("Delete Project", self)
        current_row = table.currentRow()

        def do_edit():
            open_projects = [p for p in self.projects if p.status == "Open"]
            if 0 <= current_row < len(open_projects):
                project = open_projects[current_row]
                old_name = project.name
                new_name, ok = QInputDialog.getText(self, "Edit Project", "Enter new name:", text=old_name)
                if ok and new_name.strip():
                    project.name = new_name
                    self.dc.save_project(project)
                    QMessageBox.information(self, "Success", "Project updated.")
                self.show_projects_open()

        def do_delete():
            open_projects = [p for p in self.projects if p.status == "Open"]
            if 0 <= current_row < len(open_projects):
                reply = QMessageBox.question(
                    self, "Confirm", "Are you sure to remove this project?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    proj = open_projects[current_row]
                    self.projects.remove(proj)
                    self.dc.save_all_projects(self.projects)
                    self.show_projects_open()

        act_edit.triggered.connect(do_edit)
        act_delete.triggered.connect(do_delete)
        menu.addAction(act_edit)
        menu.addAction(act_delete)
        menu.exec(table.mapToGlobal(pos))

    def edit_assignment_for_project_open(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = EditAssignmentDialog(self, project)
        dlg.exec()
        self.dc.save_all_projects(self.projects)
        self.show_projects_open()

    def open_project_details_open(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = ProjectDetailsDialog(project, self)
        dlg.exec()


    def setup_tab_pending(self):
        """Giả sử trong .ui có tableWidgetPending, lineEditSearchPending, pushButtonPendingAddTask, ..."""
        if hasattr(self, "pushButtonPendingAddTask"):
            self.pushButtonPendingAddTask.clicked.connect(self.open_add_project_pending)
        if hasattr(self, "pushButtonPendingDelete"):
            self.pushButtonPendingDelete.clicked.connect(self.remove_selected_projects_pending)
        if hasattr(self, "pushButtonPendingSearch"):
            self.pushButtonPendingSearch.clicked.connect(self.filter_projects_pending)
        if hasattr(self, "pushButtonPendingReload"):
            self.pushButtonPendingReload.clicked.connect(self.reset_filter_pending)
        if hasattr(self, "checkBoxSelectAllPending"):
            self.checkBoxSelectAllPending.stateChanged.connect(self.select_all_projects_pending)

        if hasattr(self, "tableWidgetPending"):
            self.tableWidgetPending.setColumnCount(14)
            self.tableWidgetPending.setHorizontalHeaderLabels([
                "Select", "ID", "Name", "Assignment", "Manager",
                "Status", "Progress", "Start Date", "End Date",
                "Priority", "Dependency", "Description", "Attachments", "Details"
            ])
            self.tableWidgetPending.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.tableWidgetPending.customContextMenuRequested.connect(self.show_context_menu_pending)

        self.show_projects_pending()

    def show_projects_pending(self):
        """Hiển thị project có status == 'Pending'."""
        if not hasattr(self, "tableWidgetPending"):
            return
        table = self.tableWidgetPending
        table.setRowCount(0)
        pending_projects = [p for p in self.projects if p.status == "Pending"]
        for row, project in enumerate(pending_projects):
            table.insertRow(row)
            cb = QCheckBox()
            table.setCellWidget(row, 0, cb)
            table.setItem(row, 1, QTableWidgetItem(project.project_id))
            table.setItem(row, 2, QTableWidgetItem(project.name))

            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project_pending)
            table.setCellWidget(row, 3, btn_assign)

            table.setItem(row, 4, QTableWidgetItem(project.manager))

            combo = self.create_status_combo(project, refresh_fn=self.show_projects_pending)
            table.setCellWidget(row, 5, combo)

            prog_widget = self.create_progress_widget(project, refresh_fn=self.show_projects_pending)
            table.setCellWidget(row, 6, prog_widget)

            table.setItem(row, 7, QTableWidgetItem(project.start_date))
            table.setItem(row, 8, QTableWidgetItem(project.end_date))
            table.setItem(row, 9, QTableWidgetItem(project.priority))
            dep = project.dependency or ""
            table.setItem(row, 10, QTableWidgetItem(dep))
            table.setItem(row, 11, QTableWidgetItem(project.description))

            attach_str = ", ".join(project.attachments) if project.attachments else ""
            table.setItem(row, 12, QTableWidgetItem(attach_str))

            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details_pending)
            table.setCellWidget(row, 13, btn_details)

    def open_add_project_pending(self):
        self.mainwindow_pending = QMainWindow()
        self.myui_pending = AddProjectWindowNewExt(onProjectAdded=self.load_projects_pending)
        self.myui_pending.setupUi(self.mainwindow_pending)
        self.mainwindow_pending.show()

    def load_projects_pending(self, new_project=None):
        self.projects = self.dc.get_all_projects() or []
        self.show_projects_pending()

    def remove_selected_projects_pending(self):
        if not hasattr(self, "tableWidgetPending"):
            return
        table = self.tableWidgetPending
        selected_rows = []
        for row in range(table.rowCount()):
            w = table.cellWidget(row, 0)
            if isinstance(w, QCheckBox) and w.isChecked():
                selected_rows.append(row)
        pending_projects = [p for p in self.projects if p.status == "Pending"]
        for row in reversed(selected_rows):
            if row < len(pending_projects):
                proj = pending_projects[row]
                self.projects.remove(proj)
                self.add_notification("Deleted", proj, self.current_user)
        self.dc.save_all_projects(self.projects)
        self.show_projects_pending()

    def filter_projects_pending(self):
        if not hasattr(self, "lineEditSearchPending"):
            return
        query = self.lineEditSearchPending.text().strip().lower()
        if not query:
            self.show_projects_pending()
            return
        pending_projects = [p for p in self.projects if p.status == "Pending"]
        filtered = [p for p in pending_projects if query in p.project_id.lower() or query in p.name.lower()]
        self.show_filtered_projects_pending(filtered)

    def show_filtered_projects_pending(self, projs):
        table = self.tableWidgetPending
        table.setRowCount(0)
        for row, project in enumerate(projs):
            table.insertRow(row)
            cb = QCheckBox()
            table.setCellWidget(row, 0, cb)
            table.setItem(row, 1, QTableWidgetItem(project.project_id))
            table.setItem(row, 2, QTableWidgetItem(project.name))

            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project_pending)
            table.setCellWidget(row, 3, btn_assign)

            table.setItem(row, 4, QTableWidgetItem(project.manager))

            combo = self.create_status_combo(project, refresh_fn=self.show_projects_pending)
            table.setCellWidget(row, 5, combo)

            prog_widget = self.create_progress_widget(project, refresh_fn=self.show_projects_pending)
            table.setCellWidget(row, 6, prog_widget)

            table.setItem(row, 7, QTableWidgetItem(project.start_date))
            table.setItem(row, 8, QTableWidgetItem(project.end_date))
            table.setItem(row, 9, QTableWidgetItem(project.priority))
            table.setItem(row, 10, QTableWidgetItem(project.dependency or ""))
            table.setItem(row, 11, QTableWidgetItem(project.description))

            attach_str = ", ".join(project.attachments) if project.attachments else ""
            table.setItem(row, 12, QTableWidgetItem(attach_str))

            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details_pending)
            table.setCellWidget(row, 13, btn_details)

    def reset_filter_pending(self):
        if hasattr(self, "lineEditSearchPending"):
            self.lineEditSearchPending.clear()
        self.show_projects_pending()

    def select_all_projects_pending(self, state):
        if not hasattr(self, "tableWidgetPending"):
            return
        table = self.tableWidgetPending
        for row in range(table.rowCount()):
            w = table.cellWidget(row, 0)
            if isinstance(w, QCheckBox):
                w.setChecked(state == Qt.CheckState.Checked.value)

    def show_context_menu_pending(self, pos):
        if not hasattr(self, "tableWidgetPending"):
            return
        table = self.tableWidgetPending
        menu = QMenu(self)
        act_edit = QAction("Edit Project", self)
        act_delete = QAction("Delete Project", self)

        current_row = table.currentRow()

        def do_edit():
            pending_projects = [p for p in self.projects if p.status == "Pending"]
            if 0 <= current_row < len(pending_projects):
                project = pending_projects[current_row]
                old_name = project.name
                new_name, ok = QInputDialog.getText(self, "Edit Project", "Enter new name:", text=old_name)
                if ok and new_name.strip():
                    project.name = new_name
                    self.dc.save_project(project)
                    QMessageBox.information(self, "Success", "Project updated.")
                self.show_projects_pending()

        def do_delete():
            pending_projects = [p for p in self.projects if p.status == "Pending"]
            if 0 <= current_row < len(pending_projects):
                reply = QMessageBox.question(
                    self, "Confirm", "Are you sure to remove this project?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    proj = pending_projects[current_row]
                    self.projects.remove(proj)
                    self.dc.save_all_projects(self.projects)
                    self.show_projects_pending()

        act_edit.triggered.connect(do_edit)
        act_delete.triggered.connect(do_delete)
        menu.addAction(act_edit)
        menu.addAction(act_delete)
        menu.exec(table.mapToGlobal(pos))

    def edit_assignment_for_project_pending(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = EditAssignmentDialog(self, project)
        dlg.exec()
        self.dc.save_all_projects(self.projects)
        self.show_projects_pending()

    def open_project_details_pending(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = ProjectDetailsDialog(project, self)
        dlg.exec()


    def setup_tab_ongoing(self):
        if hasattr(self, "pushButtonOngoingAddTask"):
            self.pushButtonOngoingAddTask.clicked.connect(self.open_add_project_ongoing)
        if hasattr(self, "pushButtonOngoingDelete"):
            self.pushButtonOngoingDelete.clicked.connect(self.remove_selected_projects_ongoing)
        if hasattr(self, "pushButtonOngoingSearch"):
            self.pushButtonOngoingSearch.clicked.connect(self.filter_projects_ongoing)
        if hasattr(self, "pushButtonOngoingReload"):
            self.pushButtonOngoingReload.clicked.connect(self.reset_filter_ongoing)
        if hasattr(self, "checkBoxSelectAllOngoing"):
            self.checkBoxSelectAllOngoing.stateChanged.connect(self.select_all_projects_ongoing)
        if hasattr(self, "tableWidgetOngoing"):
            self.tableWidgetOngoing.setColumnCount(14)
            self.tableWidgetOngoing.setHorizontalHeaderLabels([
                "Select", "ID", "Name", "Assignment", "Manager",
                "Status", "Progress", "Start Date", "End Date",
                "Priority", "Dependency", "Description", "Attachments", "Details"
            ])
            self.tableWidgetOngoing.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.tableWidgetOngoing.customContextMenuRequested.connect(self.show_context_menu_ongoing)
        self.show_projects_ongoing()

    def show_projects_ongoing(self):
        if not hasattr(self, "tableWidgetOngoing"):
            return
        table = self.tableWidgetOngoing
        table.setRowCount(0)
        ongoing_projects = [p for p in self.projects if p.status == "Ongoing"]
        for row, project in enumerate(ongoing_projects):
            table.insertRow(row)
            cb = QCheckBox()
            table.setCellWidget(row, 0, cb)
            table.setItem(row, 1, QTableWidgetItem(project.project_id))
            table.setItem(row, 2, QTableWidgetItem(project.name))
            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project_ongoing)
            table.setCellWidget(row, 3, btn_assign)
            table.setItem(row, 4, QTableWidgetItem(project.manager))
            combo = self.create_status_combo(project, refresh_fn=self.show_projects_ongoing)
            table.setCellWidget(row, 5, combo)
            prog_widget = self.create_progress_widget(project, refresh_fn=self.show_projects_ongoing)
            table.setCellWidget(row, 6, prog_widget)
            table.setItem(row, 7, QTableWidgetItem(project.start_date))
            table.setItem(row, 8, QTableWidgetItem(project.end_date))
            table.setItem(row, 9, QTableWidgetItem(project.priority))
            dep = project.dependency or ""
            table.setItem(row, 10, QTableWidgetItem(dep))
            table.setItem(row, 11, QTableWidgetItem(project.description))
            attach_str = ", ".join(project.attachments) if project.attachments else ""
            table.setItem(row, 12, QTableWidgetItem(attach_str))
            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details_ongoing)
            table.setCellWidget(row, 13, btn_details)

    def open_add_project_ongoing(self):
        self.mainwindow_ongoing = QMainWindow()
        self.myui_ongoing = AddProjectWindowNewExt(onProjectAdded=self.load_projects_ongoing)
        self.myui_ongoing.setupUi(self.mainwindow_ongoing)
        self.mainwindow_ongoing.show()

    def load_projects_ongoing(self, new_project=None):
        self.projects = self.dc.get_all_projects() or []
        self.show_projects_ongoing()

    def remove_selected_projects_ongoing(self):
        if not hasattr(self, "tableWidgetOngoing"):
            return
        table = self.tableWidgetOngoing
        selected_rows = []
        for row in range(table.rowCount()):
            w = table.cellWidget(row, 0)
            if isinstance(w, QCheckBox) and w.isChecked():
                selected_rows.append(row)
        ongoing_projects = [p for p in self.projects if p.status == "Ongoing"]
        for row in reversed(selected_rows):
            if row < len(ongoing_projects):
                proj = ongoing_projects[row]
                self.projects.remove(proj)
                self.add_notification("Deleted", proj, self.current_user)
        self.dc.save_all_projects(self.projects)
        self.show_projects_ongoing()

    def filter_projects_ongoing(self):
        if not hasattr(self, "lineEditSearchOngoing"):
            return
        query = self.lineEditSearchOngoing.text().strip().lower()
        if not query:
            self.show_projects_ongoing()
            return
        ongoing_projects = [p for p in self.projects if p.status == "Ongoing"]
        filtered = [p for p in ongoing_projects if query in p.project_id.lower() or query in p.name.lower()]
        self.show_filtered_projects_ongoing(filtered)

    def show_filtered_projects_ongoing(self, projs):
        table = self.tableWidgetOngoing
        table.setRowCount(0)
        for row, project in enumerate(projs):
            table.insertRow(row)
            cb = QCheckBox()
            table.setCellWidget(row, 0, cb)
            table.setItem(row, 1, QTableWidgetItem(project.project_id))
            table.setItem(row, 2, QTableWidgetItem(project.name))
            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project_ongoing)
            table.setCellWidget(row, 3, btn_assign)
            table.setItem(row, 4, QTableWidgetItem(project.manager))
            combo = self.create_status_combo(project, refresh_fn=self.show_projects_ongoing)
            table.setCellWidget(row, 5, combo)
            prog_widget = self.create_progress_widget(project, refresh_fn=self.show_projects_ongoing)
            table.setCellWidget(row, 6, prog_widget)
            table.setItem(row, 7, QTableWidgetItem(project.start_date))
            table.setItem(row, 8, QTableWidgetItem(project.end_date))
            table.setItem(row, 9, QTableWidgetItem(project.priority))
            dep = project.dependency or ""
            table.setItem(row, 10, QTableWidgetItem(dep))
            table.setItem(row, 11, QTableWidgetItem(project.description))
            attach_str = ", ".join(project.attachments) if project.attachments else ""
            table.setItem(row, 12, QTableWidgetItem(attach_str))
            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details_ongoing)
            table.setCellWidget(row, 13, btn_details)

    def reset_filter_ongoing(self):
        if hasattr(self, "lineEditSearchOngoing"):
            self.lineEditSearchOngoing.clear()
        self.show_projects_ongoing()

    def select_all_projects_ongoing(self, state):
        if not hasattr(self, "tableWidgetOngoing"):
            return
        table = self.tableWidgetOngoing
        for row in range(table.rowCount()):
            w = table.cellWidget(row, 0)
            if isinstance(w, QCheckBox):
                w.setChecked(state == Qt.CheckState.Checked.value)

    def show_context_menu_ongoing(self, pos):
        if not hasattr(self, "tableWidgetOngoing"):
            return
        table = self.tableWidgetOngoing
        menu = QMenu(self)
        act_edit = QAction("Edit Project", self)
        act_delete = QAction("Delete Project", self)
        current_row = table.currentRow()

        def do_edit():
            ongoing_projects = [p for p in self.projects if p.status == "Ongoing"]
            if 0 <= current_row < len(ongoing_projects):
                project = ongoing_projects[current_row]
                old_name = project.name
                new_name, ok = QInputDialog.getText(self, "Edit Project", "Enter new name:", text=old_name)
                if ok and new_name.strip():
                    project.name = new_name
                    self.dc.save_project(project)
                    QMessageBox.information(self, "Success", "Project updated.")
                self.show_projects_ongoing()

        def do_delete():
            ongoing_projects = [p for p in self.projects if p.status == "Ongoing"]
            if 0 <= current_row < len(ongoing_projects):
                reply = QMessageBox.question(self, "Confirm", "Are you sure to remove this project?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                             QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    proj = ongoing_projects[current_row]
                    self.projects.remove(proj)
                    self.dc.save_all_projects(self.projects)
                    self.show_projects_ongoing()

        act_edit.triggered.connect(do_edit)
        act_delete.triggered.connect(do_delete)
        menu.addAction(act_edit)
        menu.addAction(act_delete)
        menu.exec(table.mapToGlobal(pos))

    def edit_assignment_for_project_ongoing(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = EditAssignmentDialog(self, project)
        dlg.exec()
        self.dc.save_all_projects(self.projects)
        self.show_projects_ongoing()

    def open_project_details_ongoing(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = ProjectDetailsDialog(project, self)
        dlg.exec()

    def setup_tab_completed(self):
        if hasattr(self, "pushButtonCompletedAddTask"):
            self.pushButtonCompletedAddTask.clicked.connect(self.open_add_project_completed)
        if hasattr(self, "pushButtonCompletedDelete"):
            self.pushButtonCompletedDelete.clicked.connect(self.remove_selected_projects_completed)
        if hasattr(self, "pushButtonCompletedSearch"):
            self.pushButtonCompletedSearch.clicked.connect(self.filter_projects_completed)
        if hasattr(self, "pushButtonCompletedReload"):
            self.pushButtonCompletedReload.clicked.connect(self.reset_filter_completed)
        if hasattr(self, "checkBoxSelectAllCompleted"):
            self.checkBoxSelectAllCompleted.stateChanged.connect(self.select_all_projects_completed)

        if hasattr(self, "tableWidgetCompleted"):
            self.tableWidgetCompleted.setColumnCount(14)
            self.tableWidgetCompleted.setHorizontalHeaderLabels([
                "Select", "ID", "Name", "Assignment", "Manager",
                "Status", "Progress", "Start Date", "End Date",
                "Priority", "Dependency", "Description", "Attachments", "Details"
            ])
            self.tableWidgetCompleted.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.tableWidgetCompleted.customContextMenuRequested.connect(self.show_context_menu_completed)
        self.show_projects_completed()

    def show_projects_completed(self):
        if not hasattr(self, "tableWidgetCompleted"):
            return
        table = self.tableWidgetCompleted
        table.setRowCount(0)
        completed_projects = [p for p in self.projects if p.status == "Completed"]
        for row, project in enumerate(completed_projects):
            table.insertRow(row)
            cb = QCheckBox()
            table.setCellWidget(row, 0, cb)
            table.setItem(row, 1, QTableWidgetItem(project.project_id))
            table.setItem(row, 2, QTableWidgetItem(project.name))
            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project_completed)
            table.setCellWidget(row, 3, btn_assign)
            table.setItem(row, 4, QTableWidgetItem(project.manager))
            combo = self.create_status_combo(project, refresh_fn=self.show_projects_completed)
            table.setCellWidget(row, 5, combo)
            prog_widget = self.create_progress_widget(project, refresh_fn=self.show_projects_completed)
            table.setCellWidget(row, 6, prog_widget)
            table.setItem(row, 7, QTableWidgetItem(project.start_date))
            table.setItem(row, 8, QTableWidgetItem(project.end_date))
            table.setItem(row, 9, QTableWidgetItem(project.priority))
            dep = project.dependency or ""
            table.setItem(row, 10, QTableWidgetItem(dep))
            table.setItem(row, 11, QTableWidgetItem(project.description))
            attach_str = ", ".join(project.attachments) if project.attachments else ""
            table.setItem(row, 12, QTableWidgetItem(attach_str))
            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details_completed)
            table.setCellWidget(row, 13, btn_details)

    def open_add_project_completed(self):
        self.mainwindow_completed = QMainWindow()
        self.myui_completed = AddProjectWindowNewExt(onProjectAdded=self.load_projects_completed)
        self.myui_completed.setupUi(self.mainwindow_completed)
        self.mainwindow_completed.show()

    def load_projects_completed(self, new_project=None):
        self.projects = self.dc.get_all_projects() or []
        self.show_projects_completed()

    def remove_selected_projects_completed(self):
        if not hasattr(self, "tableWidgetCompleted"):
            return
        table = self.tableWidgetCompleted
        selected_rows = []
        for row in range(table.rowCount()):
            w = table.cellWidget(row, 0)
            if isinstance(w, QCheckBox) and w.isChecked():
                selected_rows.append(row)
        completed_projects = [p for p in self.projects if p.status == "Completed"]
        for row in reversed(selected_rows):
            if row < len(completed_projects):
                proj = completed_projects[row]
                self.projects.remove(proj)
                self.add_notification("Deleted", proj, self.current_user)
        self.dc.save_all_projects(self.projects)
        self.show_projects_completed()

    def filter_projects_completed(self):
        if not hasattr(self, "lineEditSearchCompleted"):
            return
        query = self.lineEditSearchCompleted.text().strip().lower()
        if not query:
            self.show_projects_completed()
            return
        completed_projects = [p for p in self.projects if p.status == "Completed"]
        filtered = [p for p in completed_projects if query in p.project_id.lower() or query in p.name.lower()]
        self.show_filtered_projects_completed(filtered)

    def show_filtered_projects_completed(self, projs):
        table = self.tableWidgetCompleted
        table.setRowCount(0)
        for row, project in enumerate(projs):
            table.insertRow(row)
            cb = QCheckBox()
            table.setCellWidget(row, 0, cb)
            table.setItem(row, 1, QTableWidgetItem(project.project_id))
            table.setItem(row, 2, QTableWidgetItem(project.name))
            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project_completed)
            table.setCellWidget(row, 3, btn_assign)
            table.setItem(row, 4, QTableWidgetItem(project.manager))
            combo = self.create_status_combo(project, refresh_fn=self.show_projects_completed)
            table.setCellWidget(row, 5, combo)
            prog_widget = self.create_progress_widget(project, refresh_fn=self.show_projects_completed)
            table.setCellWidget(row, 6, prog_widget)
            table.setItem(row, 7, QTableWidgetItem(project.start_date))
            table.setItem(row, 8, QTableWidgetItem(project.end_date))
            table.setItem(row, 9, QTableWidgetItem(project.priority))
            dep = project.dependency or ""
            table.setItem(row, 10, QTableWidgetItem(dep))
            table.setItem(row, 11, QTableWidgetItem(project.description))
            attach_str = ", ".join(project.attachments) if project.attachments else ""
            table.setItem(row, 12, QTableWidgetItem(attach_str))
            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details_completed)
            table.setCellWidget(row, 13, btn_details)

    def reset_filter_completed(self):
        if hasattr(self, "lineEditSearchCompleted"):
            self.lineEditSearchCompleted.clear()
        self.show_projects_completed()

    def select_all_projects_completed(self, state):
        if not hasattr(self, "tableWidgetCompleted"):
            return
        table = self.tableWidgetCompleted
        for row in range(table.rowCount()):
            w = table.cellWidget(row, 0)
            if isinstance(w, QCheckBox):
                w.setChecked(state == Qt.CheckState.Checked.value)

    def show_context_menu_completed(self, pos):
        if not hasattr(self, "tableWidgetCompleted"):
            return
        table = self.tableWidgetCompleted
        menu = QMenu(self)
        act_edit = QAction("Edit Project", self)
        act_delete = QAction("Delete Project", self)
        current_row = table.currentRow()

        def do_edit():
            completed_projects = [p for p in self.projects if p.status == "Completed"]
            if 0 <= current_row < len(completed_projects):
                project = completed_projects[current_row]
                old_name = project.name
                new_name, ok = QInputDialog.getText(self, "Edit Project", "Enter new name:", text=old_name)
                if ok and new_name.strip():
                    project.name = new_name
                    self.dc.save_project(project)
                    QMessageBox.information(self, "Success", "Project updated.")
                self.show_projects_completed()

        def do_delete():
            completed_projects = [p for p in self.projects if p.status == "Completed"]
            if 0 <= current_row < len(completed_projects):
                reply = QMessageBox.question(
                    self, "Confirm", "Are you sure to remove this project?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    proj = completed_projects[current_row]
                    self.projects.remove(proj)
                    self.dc.save_all_projects(self.projects)
                    self.show_projects_completed()

        act_edit.triggered.connect(do_edit)
        act_delete.triggered.connect(do_delete)
        menu.addAction(act_edit)
        menu.addAction(act_delete)
        menu.exec(table.mapToGlobal(pos))

    def edit_assignment_for_project_completed(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = EditAssignmentDialog(self, project)
        dlg.exec()
        self.dc.save_all_projects(self.projects)
        self.show_projects_completed()

    def open_project_details_completed(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = ProjectDetailsDialog(project, self)
        dlg.exec()

    def setup_tab_canceled(self):
        if hasattr(self, "pushButtonCanceledAddTask"):
            self.pushButtonCanceledAddTask.clicked.connect(self.open_add_project_canceled)
        if hasattr(self, "pushButtonCanceledDelete"):
            self.pushButtonCanceledDelete.clicked.connect(self.remove_selected_projects_canceled)
        if hasattr(self, "pushButtonCanceledSearch"):
            self.pushButtonCanceledSearch.clicked.connect(self.filter_projects_canceled)
        if hasattr(self, "pushButtonCanceledReload"):
            self.pushButtonCanceledReload.clicked.connect(self.reset_filter_canceled)
        if hasattr(self, "checkBoxSelectAllCanceled"):
            self.checkBoxSelectAllCanceled.stateChanged.connect(self.select_all_projects_canceled)

        if hasattr(self, "tableWidgetCanceled"):
            self.tableWidgetCanceled.setColumnCount(14)
            self.tableWidgetCanceled.setHorizontalHeaderLabels([
                "Select", "ID", "Name", "Assignment", "Manager",
                "Status", "Progress", "Start Date", "End Date",
                "Priority", "Dependency", "Description", "Attachments", "Details"
            ])
            self.tableWidgetCanceled.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.tableWidgetCanceled.customContextMenuRequested.connect(self.show_context_menu_canceled)
        self.show_projects_canceled()

    def show_projects_canceled(self):
        if not hasattr(self, "tableWidgetCanceled"):
            return
        table = self.tableWidgetCanceled
        table.setRowCount(0)
        canceled_projects = [p for p in self.projects if p.status == "Canceled"]
        for row, project in enumerate(canceled_projects):
            table.insertRow(row)
            cb = QCheckBox()
            table.setCellWidget(row, 0, cb)
            table.setItem(row, 1, QTableWidgetItem(project.project_id))
            table.setItem(row, 2, QTableWidgetItem(project.name))
            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project_canceled)
            table.setCellWidget(row, 3, btn_assign)
            table.setItem(row, 4, QTableWidgetItem(project.manager))
            combo = self.create_status_combo(project, refresh_fn=self.show_projects_canceled)
            table.setCellWidget(row, 5, combo)
            prog_widget = self.create_progress_widget(project, refresh_fn=self.show_projects_canceled)
            table.setCellWidget(row, 6, prog_widget)
            table.setItem(row, 7, QTableWidgetItem(project.start_date))
            table.setItem(row, 8, QTableWidgetItem(project.end_date))
            table.setItem(row, 9, QTableWidgetItem(project.priority))
            dep = project.dependency or ""
            table.setItem(row, 10, QTableWidgetItem(dep))
            table.setItem(row, 11, QTableWidgetItem(project.description))
            attach_str = ", ".join(project.attachments) if project.attachments else ""
            table.setItem(row, 12, QTableWidgetItem(attach_str))
            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details_canceled)
            table.setCellWidget(row, 13, btn_details)

    def open_add_project_canceled(self):
        self.mainwindow_canceled = QMainWindow()
        self.myui_canceled = AddProjectWindowNewExt(onProjectAdded=self.load_projects_canceled)
        self.myui_canceled.setupUi(self.mainwindow_canceled)
        self.mainwindow_canceled.show()

    def load_projects_canceled(self, new_project=None):
        self.projects = self.dc.get_all_projects() or []
        self.show_projects_canceled()

    def remove_selected_projects_canceled(self):
        if not hasattr(self, "tableWidgetCanceled"):
            return
        table = self.tableWidgetCanceled
        selected_rows = []
        for row in range(table.rowCount()):
            w = table.cellWidget(row, 0)
            if isinstance(w, QCheckBox) and w.isChecked():
                selected_rows.append(row)
        canceled_projects = [p for p in self.projects if p.status == "Canceled"]
        for row in reversed(selected_rows):
            if row < len(canceled_projects):
                proj = canceled_projects[row]
                self.projects.remove(proj)
                self.add_notification("Deleted", proj, self.current_user)
        self.dc.save_all_projects(self.projects)
        self.show_projects_canceled()

    def filter_projects_canceled(self):
        if not hasattr(self, "lineEditSearchCanceled"):
            return
        query = self.lineEditSearchCanceled.text().strip().lower()
        if not query:
            self.show_projects_canceled()
            return
        canceled_projects = [p for p in self.projects if p.status == "Canceled"]
        filtered = [p for p in canceled_projects if query in p.project_id.lower() or query in p.name.lower()]
        self.show_filtered_projects_canceled(filtered)

    def show_filtered_projects_canceled(self, projs):
        table = self.tableWidgetCanceled
        table.setRowCount(0)
        for row, project in enumerate(projs):
            table.insertRow(row)
            cb = QCheckBox()
            table.setCellWidget(row, 0, cb)
            table.setItem(row, 1, QTableWidgetItem(project.project_id))
            table.setItem(row, 2, QTableWidgetItem(project.name))
            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project_canceled)
            table.setCellWidget(row, 3, btn_assign)
            table.setItem(row, 4, QTableWidgetItem(project.manager))
            combo = self.create_status_combo(project, refresh_fn=self.show_projects_canceled)
            table.setCellWidget(row, 5, combo)
            prog_widget = self.create_progress_widget(project, refresh_fn=self.show_projects_canceled)
            table.setCellWidget(row, 6, prog_widget)
            table.setItem(row, 7, QTableWidgetItem(project.start_date))
            table.setItem(row, 8, QTableWidgetItem(project.end_date))
            table.setItem(row, 9, QTableWidgetItem(project.priority))
            dep = project.dependency or ""
            table.setItem(row, 10, QTableWidgetItem(dep))
            table.setItem(row, 11, QTableWidgetItem(project.description))
            attach_str = ", ".join(project.attachments) if project.attachments else ""
            table.setItem(row, 12, QTableWidgetItem(attach_str))
            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details_canceled)
            table.setCellWidget(row, 13, btn_details)

    def reset_filter_canceled(self):
        if hasattr(self, "lineEditSearchCanceled"):
            self.lineEditSearchCanceled.clear()
        self.show_projects_canceled()

    def select_all_projects_canceled(self, state):
        if not hasattr(self, "tableWidgetCanceled"):
            return
        table = self.tableWidgetCanceled
        for row in range(table.rowCount()):
            w = table.cellWidget(row, 0)
            if isinstance(w, QCheckBox):
                w.setChecked(state == Qt.CheckState.Checked.value)

    def show_context_menu_canceled(self, pos):
        if not hasattr(self, "tableWidgetCanceled"):
            return
        table = self.tableWidgetCanceled
        menu = QMenu(self)
        act_edit = QAction("Edit Project", self)
        act_delete = QAction("Delete Project", self)
        current_row = table.currentRow()

        def do_edit():
            canceled_projects = [p for p in self.projects if p.status == "Canceled"]
            if 0 <= current_row < len(canceled_projects):
                project = canceled_projects[current_row]
                old_name = project.name
                new_name, ok = QInputDialog.getText(self, "Edit Project", "Enter new name:", text=old_name)
                if ok and new_name.strip():
                    project.name = new_name
                    self.dc.save_project(project)
                    QMessageBox.information(self, "Success", "Project updated.")
                self.show_projects_canceled()

        def do_delete():
            canceled_projects = [p for p in self.projects if p.status == "Canceled"]
            if 0 <= current_row < len(canceled_projects):
                reply = QMessageBox.question(
                    self, "Confirm", "Are you sure to remove this project?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    proj = canceled_projects[current_row]
                    self.projects.remove(proj)
                    self.dc.save_all_projects(self.projects)
                    self.show_projects_canceled()

        act_edit.triggered.connect(do_edit)
        act_delete.triggered.connect(do_delete)
        menu.addAction(act_edit)
        menu.addAction(act_delete)
        menu.exec(table.mapToGlobal(pos))

    def edit_assignment_for_project_canceled(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = EditAssignmentDialog(self, project)
        dlg.exec()
        self.dc.save_all_projects(self.projects)
        self.show_projects_canceled()

    def open_project_details_canceled(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = ProjectDetailsDialog(project, self)
        dlg.exec()


    # Gantt tab
    def setup_gantt_tab(self):
        if hasattr(self, "tab_gantt"):
            layout = QVBoxLayout(self.tab_gantt)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            # Đồng hồ
            self.clock_widget = ClockWidget()
            layout.addWidget(self.clock_widget, alignment=Qt.AlignmentFlag.AlignRight)

            # Thay vì self.gantt_view = GanttTimeLineView(),
            # ta dùng container:
            self.gantt_container = GanttContainer()
            self.gantt_container.set_projects(self.projects)

            layout.addWidget(self.gantt_container)

    def setup_account_tab(self):
        if hasattr(self, "pushButtonChangePhoto"):
            self.pushButtonChangePhoto.clicked.connect(self.change_photo)
        if hasattr(self, "pushButtonRemovePhoto"):
            self.pushButtonRemovePhoto.clicked.connect(self.remove_photo)
        if hasattr(self, "pushButtonChangeEmail"):
            self.pushButtonChangeEmail.clicked.connect(self.change_email)
        if hasattr(self, "pushButtonDeleteAccount"):
            self.pushButtonDeleteAccount.clicked.connect(self.delete_account)
        if hasattr(self, "pushButtonLogOut"):
            self.pushButtonLogOut.clicked.connect(self.log_out)
        if hasattr(self, "pushButtonAddPassword"):
            self.pushButtonAddPassword.clicked.connect(self.change_password)

    def change_password(self):
        """Open 'Forgot Password' window."""
        from ui.ForgotPassWindow.ForgotPasswordWindowExt import ForgotPasswordWindowExt
        self.MainWindow.close()
        self.mainwindow = QMainWindow()
        self.myui = ForgotPasswordWindowExt()
        self.myui.setupUi(self.mainwindow)
        self.myui.showWindow()

    def update_account_display(self):
        if not self.current_user:
            return
        if hasattr(self, "lblAvatar"):
            if self.current_user.Avatar and os.path.exists(self.current_user.Avatar):
                pix = QPixmap(self.current_user.Avatar)
            else:
                pix = QPixmap("D:\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\Image\avt.png")
            self.lblAvatar.setPixmap(
                pix.scaled(
                    self.lblAvatar.width(),
                    self.lblAvatar.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        if hasattr(self, "lineEditName"):
            self.lineEditName.setText(self.current_user.Name)
        if hasattr(self, "lineEditEmail"):
            self.lineEditEmail.setText(self.current_user.Email)

    def change_photo(self):
        if not self.current_user:
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self.MainWindow,
            "Select Avatar Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.current_user.Avatar = file_path
            self.save_current_user()
            self.update_account_display()

    def remove_photo(self):
        if not self.current_user:
            return
        self.current_user.Avatar = None
        self.save_current_user()
        self.update_account_display()

    def change_email(self):
        if not self.current_user:
            return
        if not hasattr(self, "lineEditEmail"):
            return
        new_email = self.lineEditEmail.text().strip().lower()
        if not new_email:
            QMessageBox.warning(self.MainWindow, "Invalid Email", "Email cannot be empty.")
            return
        all_users = self.dc.get_all_users()
        for u in all_users:
            if u.Username != self.current_user.Username and u.Email.strip().lower() == new_email:
                QMessageBox.warning(self.MainWindow, "Duplicate Email", "That email is already used by another user.")
                return
        self.current_user.Email = new_email
        self.save_current_user()
        QMessageBox.information(self.MainWindow, "Success", "Email updated.")
        self.update_account_display()

    def delete_account(self):
        if not self.current_user:
            return
        reply = QMessageBox.question(
            self.MainWindow,
            "Delete Account",
            "Are you sure you want to delete your account? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            all_users = self.dc.get_all_users()
            all_users = [u for u in all_users if u.Username != self.current_user.Username]
            from libs.JsonFileFactory import JsonFileFactory
            jff = JsonFileFactory()
            jff.write_data(all_users, self.dc.users_file)

            QMessageBox.information(self.MainWindow, "Account Deleted", "Your account has been deleted.")
            self.log_out()

    def log_out(self):
        QMessageBox.information(self.MainWindow, "Log Out", "You have been logged out.")
        self.MainWindow.close()
        from ui.LoginWindow.LoginMainWindowExt import LoginMainWindowExt
        self.MainWindow.close()
        self.mainwindow = QMainWindow()
        self.myui = LoginMainWindowExt()
        self.myui.setupUi(self.mainwindow)
        self.myui.showWindow()

    def save_current_user(self):
        if not self.current_user:
            return
        all_users = self.dc.get_all_users()
        found = False
        for i, u in enumerate(all_users):
            if u.Username == self.current_user.Username:
                all_users[i] = self.current_user
                found = True
                break
        if not found:
            all_users.append(self.current_user)
        from libs.JsonFileFactory import JsonFileFactory
        jff = JsonFileFactory()
        jff.write_data(all_users, self.dc.users_file)

    # Kanban
    def setup_kanban_board(self):
        self.kanban_statuses = ["Open", "Pending", "Ongoing", "Completed", "Canceled"]
        self.kanban_columns = {}
        if hasattr(self, "tab_3"):
            self.tab_3.setLayout(QHBoxLayout())
            self.tab_3.layout().setContentsMargins(10, 10, 10, 10)
            self.tab_3.layout().setSpacing(10)
            for status in self.kanban_statuses:
                col_frame = QFrame()
                col_frame.setFrameShape(QFrame.Shape.StyledPanel)
                col_layout = QVBoxLayout(col_frame)

                lbl = QLabel(status)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                col_layout.addWidget(lbl)

                column_widget = KanbanColumn(self, status, self.on_kanban_updated)
                self.kanban_columns[status] = column_widget
                col_layout.addWidget(column_widget)

                self.tab_3.layout().addWidget(col_frame)
        self.load_kanban_projects()

    def load_kanban_projects(self):
        if not hasattr(self, 'kanban_columns'):
            return
        for col in self.kanban_columns.values():
            col.clear()
        for proj in self.projects:
            item = ProjectItem(proj)
            if proj.status in self.kanban_columns:
                self.kanban_columns[proj.status].addItem(item)

    def on_kanban_updated(self):
        self.dc.save_all_projects(self.projects)
        self.update_ui()

    # Table
    def setup_table(self):
        self.tableWidgetAllProjects.setColumnCount(14)
        self.tableWidgetAllProjects.setHorizontalHeaderLabels([
            "Select", "ID", "Name", "Assignment", "Manager",
            "Status", "Progress", "Start Date", "End Date",
            "Priority", "Dependency", "Description", "Attachments", "Details"
        ])
        self.tableWidgetAllProjects.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableWidgetAllProjects.customContextMenuRequested.connect(self.show_context_menu)

    def show_projects(self):
        self.tableWidgetAllProjects.setRowCount(0)
        for row, project in enumerate(self.projects):
            self.tableWidgetAllProjects.insertRow(row)
            cb = QCheckBox()
            self.tableWidgetAllProjects.setCellWidget(row, 0, cb)

            self.tableWidgetAllProjects.setItem(row, 1, QTableWidgetItem(project.project_id))
            self.tableWidgetAllProjects.setItem(row, 2, QTableWidgetItem(project.name))

            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project)
            self.tableWidgetAllProjects.setCellWidget(row, 3, btn_assign)

            self.tableWidgetAllProjects.setItem(row, 4, QTableWidgetItem(project.manager))

            combo = self.create_status_combo(project)
            self.tableWidgetAllProjects.setCellWidget(row, 5, combo)

            prog_widget = self.create_progress_widget(project)
            self.tableWidgetAllProjects.setCellWidget(row, 6, prog_widget)

            self.tableWidgetAllProjects.setItem(row, 7, QTableWidgetItem(project.start_date))
            self.tableWidgetAllProjects.setItem(row, 8, QTableWidgetItem(project.end_date))
            self.tableWidgetAllProjects.setItem(row, 9, QTableWidgetItem(project.priority))
            dep = project.dependency or ""
            self.tableWidgetAllProjects.setItem(row, 10, QTableWidgetItem(dep))
            self.tableWidgetAllProjects.setItem(row, 11, QTableWidgetItem(project.description))

            attach_str = ", ".join(project.attachments) if project.attachments else ""
            self.tableWidgetAllProjects.setItem(row, 12, QTableWidgetItem(attach_str))

            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details)
            self.tableWidgetAllProjects.setCellWidget(row, 13, btn_details)

    def open_project_details(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = ProjectDetailsDialog(project, self.MainWindow)
        dlg.exec()

    # Charts
    def setup_charts(self):
        self.chart_layout = QVBoxLayout(self.chartWidget)
        self.chart_layout_2 = QVBoxLayout(self.chartWidget_2)
        self.draw_pie_chart()
        self.draw_line_chart()

    def draw_pie_chart(self):
        series = QPieSeries()
        status_count = {s: 0 for s in ["Open", "Pending", "Ongoing", "Completed", "Canceled"]}
        for p in self.projects:
            if p.status in status_count:
                status_count[p.status] += 1
        for s, c in status_count.items():
            if c > 0:
                series.append(f"{s} ({c})", c)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Project Status Distribution")
        chart_view = QChartView(chart)
        self.update_chart(self.chart_layout, chart_view)

    def draw_line_chart(self):
        series = QLineSeries()
        week_map = {}
        for p in self.projects:
            qd = QDate.fromString(p.start_date, "dd/MM/yyyy")
            if not qd.isValid():
                qd = QDate.fromString(p.start_date, "dd-MM-yyyy")
            if not qd.isValid():
                qd = QDate.fromString(p.start_date, "yyyy-MM-dd")
            if qd.isValid():
                w = qd.weekNumber()[0]
                week_map[w] = week_map.get(w, 0) + 1

        for w, cnt in sorted(week_map.items()):
            series.append(w, cnt)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Projects by Week")
        chart.createDefaultAxes()
        chart_view = QChartView(chart)
        self.update_chart(self.chart_layout_2, chart_view)

    def update_chart(self, layout, chart_view):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(chart_view)

    # Signals
    def setup_signals(self):
        if hasattr(self, "pushButtonAllAddTask"):
            self.pushButtonAllAddTask.clicked.connect(self.open_add_project)
        if hasattr(self, "pushButtonAllDelete"):
            self.pushButtonAllDelete.clicked.connect(self.remove_selected_projects)
        if hasattr(self, "pushButtonAllSearch"):
            self.pushButtonAllSearch.clicked.connect(self.filter_projects)
        if hasattr(self, "pushButtonAllReload"):
            self.pushButtonAllReload.clicked.connect(self.reset_filter)
        if hasattr(self, "checkBoxSelectAll"):
            self.checkBoxSelectAll.stateChanged.connect(self.select_all_projects)

    def select_all_projects(self, state):
        for row in range(self.tableWidgetAllProjects.rowCount()):
            w = self.tableWidgetAllProjects.cellWidget(row, 0)
            if isinstance(w, QCheckBox):
                w.setChecked(state == Qt.CheckState.Checked.value)

    def reset_filter(self):
        if hasattr(self, "lineEditSearchAll"):
            self.lineEditSearchAll.clear()
        self.show_projects()

    def filter_projects(self):
        query = ""
        if hasattr(self, "lineEditSearchAll"):
            query = self.lineEditSearchAll.text().strip().lower()
        if not query:
            self.show_projects()
            return
        filtered = [p for p in self.projects if query in p.project_id.lower() or query in p.name.lower()]
        self.show_filtered_projects(filtered)

    def show_filtered_projects(self, projs):
        self.tableWidgetAllProjects.setRowCount(0)
        for row, project in enumerate(projs):
            self.tableWidgetAllProjects.insertRow(row)
            cb = QCheckBox()
            self.tableWidgetAllProjects.setCellWidget(row, 0, cb)
            self.tableWidgetAllProjects.setItem(row, 1, QTableWidgetItem(project.project_id))
            self.tableWidgetAllProjects.setItem(row, 2, QTableWidgetItem(project.name))

            btn_assign = QPushButton(", ".join(project.assignment) if project.assignment else "Add People")
            btn_assign.setProperty("project_obj", project)
            btn_assign.clicked.connect(self.edit_assignment_for_project)
            self.tableWidgetAllProjects.setCellWidget(row, 3, btn_assign)

            self.tableWidgetAllProjects.setItem(row, 4, QTableWidgetItem(project.manager))

            combo = self.create_status_combo(project)
            self.tableWidgetAllProjects.setCellWidget(row, 5, combo)

            prog_widget = self.create_progress_widget(project)
            self.tableWidgetAllProjects.setCellWidget(row, 6, prog_widget)

            self.tableWidgetAllProjects.setItem(row, 7, QTableWidgetItem(project.start_date))
            self.tableWidgetAllProjects.setItem(row, 8, QTableWidgetItem(project.end_date))
            self.tableWidgetAllProjects.setItem(row, 9, QTableWidgetItem(project.priority))
            self.tableWidgetAllProjects.setItem(row, 10, QTableWidgetItem(project.dependency or ""))
            self.tableWidgetAllProjects.setItem(row, 11, QTableWidgetItem(project.description))

            attach_str = ", ".join(project.attachments) if project.attachments else ""
            self.tableWidgetAllProjects.setItem(row, 12, QTableWidgetItem(attach_str))

            btn_details = QPushButton("View Details")
            btn_details.setProperty("project_obj", project)
            btn_details.clicked.connect(self.open_project_details)
            self.tableWidgetAllProjects.setCellWidget(row, 13, btn_details)

    # CRUD
    def open_add_project(self):
        self.mainwindow = QMainWindow()
        self.myui = AddProjectWindowNewExt(onProjectAdded=self._on_project_added)
        self.myui.setupUi(self.mainwindow)
        self.myui.showWindow()

    def _on_project_added(self, new_project: Project):
        new_project.project_id = self.generate_new_project_id()
        self.dc.save_project(new_project)
        self.load_projects()
        # Ghi notification
        self.add_notification("added", new_project, self.current_user)

    def remove_selected_projects(self):
        selected_rows = []
        for row in range(self.tableWidgetAllProjects.rowCount()):
            w = self.tableWidgetAllProjects.cellWidget(row, 0)
            if isinstance(w, QCheckBox) and w.isChecked():
                selected_rows.append(row)
        for row in reversed(selected_rows):
            proj = self.projects[row]
            del self.projects[row]
            # Ghi notification
            self.add_notification("Deleted", proj, self.current_user)
        self.dc.save_all_projects(self.projects)
        self.load_projects()

    def load_projects(self):
        self.projects = self.dc.get_all_projects() or []
        self.update_ui()

    def update_ui(self):
        self.show_projects()
        self.update_project_counts()
        self.draw_pie_chart()
        self.draw_line_chart()
        self.load_kanban_projects()
        if hasattr(self, "gantt_view"):
            self.gantt_view.set_projects(self.projects)
            self.gantt_view.update()

    def edit_assignment_for_project(self):
        btn = self.sender()
        if not btn:
            return
        project = btn.property("project_obj")
        if not project:
            return
        dlg = EditAssignmentDialog(self, project)
        dlg.exec()
        self.dc.save_all_projects(self.projects)
        self.update_ui()

    def create_status_combo(self, project, refresh_fn=None):
        combo = QComboBox()
        combo.addItems(["Open", "Pending", "Ongoing", "Completed", "Canceled"])
        combo.setCurrentText(project.status)

        def on_status_changed_wrapper(new_status):
            self.on_status_changed(project, new_status)
            if refresh_fn:
                refresh_fn()

        combo.currentTextChanged.connect(on_status_changed_wrapper)
        return combo

    def on_status_changed(self, project, new_status):
        project.status = new_status
        self.dc.save_project(project)
        self.update_ui()

    def create_progress_widget(self, project, refresh_fn=None):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(project.progress)

        label = QLabel(f"{project.progress}%")

        def on_slider_changed(value):
            project.progress = value
            label.setText(f"{value}%")
            self.dc.save_project(project)
            self.update_ui()
            if refresh_fn:
                refresh_fn()  # Gọi hàm refresh_fn() nếu có

        slider.valueChanged.connect(on_slider_changed)
        layout.addWidget(slider)
        layout.addWidget(label)
        return container

    def show_context_menu(self, pos):
        menu = QMenu(self.MainWindow)
        act_edit = QAction("Edit Project", self.MainWindow)
        act_delete = QAction("Delete Project", self.MainWindow)
        current_row = self.tableWidgetAllProjects.currentRow()

        def do_edit():
            if 0 <= current_row < len(self.projects):
                project = self.projects[current_row]
                old_name = project.name
                new_name, ok = QInputDialog.getText(
                    self.MainWindow, "Edit Project", "Enter new name:", text=old_name
                )
                if ok and new_name.strip():
                    project.name = new_name
                    self.dc.save_project(project)
                    QMessageBox.information(self.MainWindow, "Success", "Project updated.")
                self.update_ui()

        def do_delete():
            if 0 <= current_row < len(self.projects):
                reply = QMessageBox.question(
                    self.MainWindow,
                    "Confirm",
                    "Are you sure to remove this project?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    del self.projects[current_row]
                    self.dc.save_all_projects(self.projects)
                    self.update_ui()

        act_edit.triggered.connect(do_edit)
        act_delete.triggered.connect(do_delete)
        menu.addAction(act_edit)
        menu.addAction(act_delete)
        menu.exec(self.tableWidgetAllProjects.mapToGlobal(pos))

    def update_project_counts(self):
        statuses = [p.status for p in self.projects]
        counts = Counter(statuses)
        for s in ["Open", "Pending", "Ongoing", "Completed", "Canceled"]:
            counts.setdefault(s, 0)

        if hasattr(self, "lblOpenCount"):
            self.lblOpenCount.setText(str(counts["Open"]))
        if hasattr(self, "lblPendingCount"):
            self.lblPendingCount.setText(str(counts["Pending"]))
        if hasattr(self, "lblOngoingCount"):
            self.lblOngoingCount.setText(str(counts["Ongoing"]))
        if hasattr(self, "lblCompletedCount"):
            self.lblCompletedCount.setText(str(counts["Completed"]))
        if hasattr(self, "lblCanceledCount"):
            self.lblCanceledCount.setText(str(counts["Canceled"]))


# ----- Entry Point -----
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)

    # Giả sử user đăng nhập
    test_user = User(
        Name="Test User",
        Email="testuser@example.com",
        PhoneNum="0123456789",
        Username="testuser",
        Password="fakehash",
        Avatar="resources/default_avatar.png"
    )

    main_win = QMainWindow()
    ui = MainWindowNewExt(main_win, current_user=test_user)
    ui.showWindow()
    sys.exit(app.exec())
