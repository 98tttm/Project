"""
Final Extended Gantt Chart Window

Features:
 - Loads projects from DataConnector.
 - Displays projects in a Gantt chart with a two-level header (Month-Year and Day rows).
 - Supports horizontal scrolling (via SHIFT+Wheel or drag).
 - Shows a real-time clock in the top bar (label_clock).
 - Double-click on a project bar shows project details.
 - Displays the number of projects in label_project_count.
 - "List" button shows a dialog with project details.
 - "Calendar" button shows a calendar dialog.
"""

import sys
from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, QTimer, QRect, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QCalendarWidget, QMessageBox
)

from libs.DataConnector import DataConnector
from ui.Gantt.GanttChartWindow import Ui_MainWindow  # This is your .ui generated Python file

# Mapping for project status to a color (for completed portion)
STATUS_COLORS = {
    "Open": "#4ECDC4",
    "Pending": "#FFAA00",
    "Ongoing": "#FF6B6B",
    "Completed": "#4CAF50",
    "Canceled": "#888888"
}
DEFAULT_REMAINING_COLOR = "#A7E9F4"


class GanttChartView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Chart configuration
        self.projects = []           # List of Project objects loaded from DataConnector
        self.days_to_show = 30       # Number of days to display horizontally
        self.cell_width = 50         # Width per day (pixels)
        self.row_height = 40         # Height per project row
        self.header_height = 70      # Total header height (split into two rows)
        self.label_width = 150       # Width of the left column (project names)

        # Default start date (will be recalculated in load_projects)
        self.start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=3)

        # DataConnector instance for project data
        self.dc = DataConnector()
        self.load_projects()
        self.update_minimum_size()

        # Timer to update time indicator every minute
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_indicator)
        self.timer.start(60000)

        # Timer for clock updates (if needed)
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_time_indicator()
        self.update_clock()

        # Variables for drag scrolling
        self.dragging = False
        self.last_mouse_pos = None

    def update_minimum_size(self):
        """Set the minimum size based on timeline and number of projects."""
        min_width = self.label_width + self.days_to_show * self.cell_width
        min_height = self.header_height + len(self.projects) * self.row_height
        self.setMinimumSize(QSize(min_width, min_height))

    def load_projects(self):
        """Load projects from DataConnector and determine the chart's start date."""
        self.projects = self.dc.get_all_projects()
        print("Projects loaded:", self.projects)
        if not self.projects:
            self.start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=3)
        else:
            try:
                earliest = min([self.parse_date(proj.start_date) for proj in self.projects])
                print("Earliest project start date:", earliest)
            except Exception as e:
                print("Error parsing project dates:", e)
                earliest = datetime.now()
            self.start_date = earliest - timedelta(days=3)
        print("Chart start date set to:", self.start_date)
        self.update_minimum_size()
        self.update()

    def parse_date(self, date_str):
        """Attempt to parse a date string using several formats."""
        formats = ["%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return datetime.now()

    def wheelEvent(self, event):
        """SHIFT+Mouse Wheel scrolls horizontally by adjusting start_date."""
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            delta = event.angleDelta().y()
            day_shift = 1 if delta > 0 else -1
            self.shift_start_date(day_shift)
            event.accept()
        else:
            super().wheelEvent(event)

    def shift_start_date(self, day_offset):
        """Shift the start_date by the given number of days."""
        self.start_date += timedelta(days=-day_offset)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.last_mouse_pos = event.position()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            dx = event.position().x() - self.last_mouse_pos.x()
            day_shift = -int(dx // self.cell_width)
            if day_shift != 0:
                self.start_date += timedelta(days=day_shift)
                self.last_mouse_pos = event.position()
                self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        # Split header into two rows: top for Month-Year, bottom for Day
        header_row1_height = self.header_height // 2
        header_row2_height = self.header_height - header_row1_height

        # 1) Overall background
        painter.fillRect(0, 0, w, h, QColor("#FFFFFF"))

        # 2) Draw header backgrounds
        painter.fillRect(0, 0, w, header_row1_height, QColor("#F5F5F5"))
        painter.fillRect(0, header_row1_height, w, header_row2_height, QColor("#F5F5F5"))

        # 3) Draw left label column (for project names)
        painter.fillRect(0, 0, self.label_width, self.header_height, QColor("#F0F0F0"))
        painter.fillRect(0, self.header_height, self.label_width, h - self.header_height, QColor("#F0F0F0"))
        painter.setPen(QPen(QColor("#CCCCCC"), 1))
        painter.drawLine(self.label_width, 0, self.label_width, h)

        # 4) Build list of days
        days = [self.start_date + timedelta(days=i) for i in range(self.days_to_show)]

        # 5) Determine month blocks for top header row
        painter.setFont(QFont("Arial", 10))
        month_blocks = []
        current_start_idx = 0
        current_month = days[0].month
        current_year = days[0].year

        for i in range(1, len(days)):
            d = days[i]
            if d.month != current_month or d.year != current_year:
                month_blocks.append((current_start_idx, i - 1, current_month, current_year))
                current_start_idx = i
                current_month = d.month
                current_year = d.year
        month_blocks.append((current_start_idx, len(days) - 1, current_month, current_year))

        # 6) Draw top header: Month-Year blocks
        for (start_idx, end_idx, mo, yr) in month_blocks:
            x_start = self.label_width + start_idx * self.cell_width
            x_end = self.label_width + (end_idx + 1) * self.cell_width
            block_width = x_end - x_start
            if block_width <= 0:
                continue
            month_name = datetime(yr, mo, 1).strftime("%b")
            text = f"{month_name} {yr}"
            painter.drawText(QRect(x_start, 0, block_width, header_row1_height),
                             Qt.AlignmentFlag.AlignCenter, text)
            # Bold vertical boundary at x_end
            painter.save()
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawLine(x_end, 0, x_end, self.header_height)
            painter.restore()

        # 7) Draw bottom header: Day numbers and short weekday
        painter.setFont(QFont("Arial", 9))
        for i, d in enumerate(days):
            x = self.label_width + i * self.cell_width
            if d.date() == datetime.now().date():
                painter.fillRect(x, header_row1_height, self.cell_width, header_row2_height, QColor("#E6F7FF"))
            day_str = str(d.day)
            day_of_week = d.strftime("%a")
            painter.drawText(QRect(x, header_row1_height, self.cell_width, 20),
                             Qt.AlignmentFlag.AlignCenter, day_str)
            painter.drawText(QRect(x, header_row1_height + 20, self.cell_width, header_row2_height - 20),
                             Qt.AlignmentFlag.AlignCenter, day_of_week)
            painter.drawLine(x, header_row1_height, x, self.header_height)

        painter.drawLine(0, self.header_height, w, self.header_height)

        # 8) Draw project names in label column (unaltered)
        painter.setFont(QFont("Arial", 9))
        for idx, project in enumerate(self.projects):
            y = self.header_height + idx * self.row_height
            painter.setPen(QColor("black"))
            painter.drawText(QRect(5, y, self.label_width - 10, self.row_height),
                             Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap,
                             project.name)

        # 9) Clip region for drawing bars (to avoid drawing over header or label column)
        painter.save()
        clip_rect = QRect(self.label_width, self.header_height, w - self.label_width, h - self.header_height)
        painter.setClipRect(clip_rect)

        # 10) Draw project bars
        for idx, project in enumerate(self.projects):
            y = self.header_height + idx * self.row_height
            sdate = self.parse_date(project.start_date)
            edate = self.parse_date(project.end_date)
            days_from_start = (sdate - self.start_date).days
            duration = (edate - sdate).days + 1
            if days_from_start < 0:
                duration += days_from_start
                days_from_start = 0
            bar_x = self.label_width + days_from_start * self.cell_width
            bar_width = duration * self.cell_width
            if bar_x < self.label_width:
                overlap = self.label_width - bar_x
                bar_x = self.label_width
                bar_width -= overlap
                if bar_width <= 0:
                    continue
            bar_rect = QRect(bar_x, y + 5, bar_width, self.row_height - 10)
            prog = int(project.progress) if isinstance(project.progress, str) else project.progress

            if prog > 0:
                pwidth = int(bar_width * prog / 100)
                project_color = getattr(project, "color", STATUS_COLORS.get(project.status, "#FF6B6B"))
                painter.fillRect(QRect(bar_x, y + 5, pwidth, self.row_height - 10), QColor(project_color))
                painter.fillRect(QRect(bar_x + pwidth, y + 5, bar_width - pwidth, self.row_height - 10),
                                 QColor(DEFAULT_REMAINING_COLOR))
            else:
                painter.fillRect(bar_rect, QColor(DEFAULT_REMAINING_COLOR))

            painter.setPen(QPen(QColor("#999999"), 1))
            painter.drawRect(bar_rect)
            painter.drawText(bar_rect, Qt.AlignmentFlag.AlignCenter, f"{prog}%")
            painter.setPen(QPen(QColor("#EEEEEE"), 1))
            painter.drawLine(self.label_width, y + self.row_height, w, y + self.row_height)
        painter.restore()

        # 11) Draw current time indicator (red vertical line)
        current_time = datetime.now()
        days_passed = (current_time - self.start_date).total_seconds() / (24 * 3600)
        time_x = self.label_width + days_passed * self.cell_width
        if 0 <= time_x <= w:
            painter.setPen(QPen(QColor("#FF0000"), 2))
            painter.drawLine(int(time_x), self.header_height, int(time_x), h)

    def update_time_indicator(self):
        self.update()

    def update_clock(self):
        # Implement if you wish to update an internal clock display
        pass

    def refresh_projects(self):
        self.load_projects()


# Extend GanttChartView with interactivity (e.g. double-click for project details)
class ClickableGanttChartView(GanttChartView):
    def mouseDoubleClickEvent(self, event):
        pos = event.pos()
        if pos.x() < self.label_width:
            return super().mouseDoubleClickEvent(event)
        row_index = (pos.y() - self.header_height) // self.row_height
        if row_index < 0 or row_index >= len(self.projects):
            return super().mouseDoubleClickEvent(event)
        project = self.projects[row_index]
        info = (
            f"Project ID: {project.project_id}\n"
            f"Name: {project.name}\n"
            f"Assignment: {', '.join(project.assignment)}\n"
            f"Manager: {project.manager}\n"
            f"Status: {project.status}\n"
            f"Progress: {project.progress}%\n"
            f"Start Date: {project.start_date}\n"
            f"End Date: {project.end_date}\n"
            f"Color: {project.color}"
        )
        QMessageBox.information(self, "Project Details", info)
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            delta = event.angleDelta().y()
            day_shift = 1 if delta > 0 else -1
            self.start_date += timedelta(days=-day_shift)
            self.update()
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.last_mouse_pos = event.position()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            dx = event.position().x() - self.last_mouse_pos.x()
            day_shift = -int(dx // self.cell_width)
            if day_shift != 0:
                self.start_date += timedelta(days=day_shift)
                self.last_mouse_pos = event.position()
                self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)


class GanttChartWindowExt(Ui_MainWindow):
    """
    Extended Gantt chart window using the UI from the .ui file.
    Loads projects from DataConnector and displays them in a Gantt chart.
    Features:
     - Real-time clock in label_clock.
     - Horizontal scrolling via SHIFT+Wheel or drag.
     - Double-click on project bars to display project details.
     - Displays number of projects in label_project_count.
     - "List" button shows a project list dialog.
     - "Calendar" button shows a calendar dialog.
    """
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.dc = DataConnector()
        self.setupSignalAndSlot()

        # Use ClickableGanttChartView for interactivity
        self.gantt_view = ClickableGanttChartView()
        self.layout_gantt = QVBoxLayout(self.widget_2)
        self.layout_gantt.setContentsMargins(0, 0, 0, 0)
        self.layout_gantt.addWidget(self.gantt_view)

        # Connect top bar buttons
        # "List" button: pushButton_3
        self.pushButton_3.clicked.connect(self.show_project_list_dialog)
        # "Calendar" button: pushButton (rename if necessary)
        self.pushButton.clicked.connect(self.show_calendar_dialog)
        # "Gantt" button: pushButton_2
        self.pushButton_2.clicked.connect(lambda: self.set_status("Gantt"))

        # Update static labels
        self.label_4.setText("Gantt Chart is displayed...")
        # Update project count
        self.update_project_count()

        # Real-time clock
        self.clock_timer = QTimer(self.MainWindow)
        self.clock_timer.timeout.connect(self.update_clock_label)
        self.clock_timer.start(1000)

    def showWindow(self):
        self.MainWindow.show()

    def setupSignalAndSlot(self):
        # Additional signals/slots can be configured here
        pass

    def set_status(self, status_text):
        print(f"Tab switched to: {status_text}")
        if status_text == "Gantt":
            self.gantt_view.refresh_projects()
            self.update_project_count()

    def refresh_gantt_chart(self):
        self.gantt_view.refresh_projects()
        self.update_project_count()

    def update_clock_label(self):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S - %d/%m/%Y")
        self.label_clock.setText(time_str)

    def update_project_count(self):
        count = len(self.gantt_view.projects)
        # Assume label_project_count exists in the UI
        self.label_project_count.setText(str(count))

    def show_project_list_dialog(self):
        """Show a dialog with a table of projects."""
        projects = self.gantt_view.projects
        dialog = QDialog(self.MainWindow)
        dialog.setWindowTitle("Project List")
        layout = QVBoxLayout(dialog)
        table = QTableWidget(dialog)
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["ID", "Name", "Status", "Progress", "Start", "End", "Manager"])
        table.setRowCount(len(projects))
        for row, p in enumerate(projects):
            table.setItem(row, 0, QTableWidgetItem(str(p.project_id)))
            table.setItem(row, 1, QTableWidgetItem(p.name))
            table.setItem(row, 2, QTableWidgetItem(p.status))
            table.setItem(row, 3, QTableWidgetItem(f"{p.progress}%"))
            table.setItem(row, 4, QTableWidgetItem(p.start_date))
            table.setItem(row, 5, QTableWidgetItem(p.end_date))
            table.setItem(row, 6, QTableWidgetItem(p.manager))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.resize(800, 400)
        dialog.exec()

    def show_calendar_dialog(self):
        """Show a dialog with a calendar widget."""
        dialog = QDialog(self.MainWindow)
        dialog.setWindowTitle("Calendar")
        vlayout = QVBoxLayout(dialog)
        calendar = QCalendarWidget(dialog)
        vlayout.addWidget(calendar)
        btn_close = QPushButton("Close", dialog)
        btn_close.clicked.connect(dialog.accept)
        vlayout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)
        dialog.setLayout(vlayout)
        dialog.resize(400, 300)
        dialog.exec()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QMainWindow, QApplication
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    ui = GanttChartWindowExt()
    ui.setupUi(main_window)
    ui.showWindow()
    sys.exit(app.exec())
