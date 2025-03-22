import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QFont


class TimeIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(3)
        self.setStyleSheet("background-color: #FF0000;")


class Task:
    def __init__(self, id, name, start_date, end_date, progress=0, color="#FF6B6B"):
        self.id = id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.progress = progress  # 0-100
        self.color = color

    def get_remaining_color(self):
        # Trả về màu nhạt hơn cho phần còn lại
        return "#A7E9F4"  # Màu xanh da trời nhạt


class GanttChartView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []
        self.days_to_show = 18  # Số ngày hiển thị
        self.cell_width = 50  # Độ rộng của mỗi ô (đại diện cho 1 ngày)
        self.row_height = 40  # Độ cao của mỗi hàng
        self.header_height = 50  # Độ cao của header
        self.label_width = 150  # Độ rộng của cột nhãn task

        self.start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.time_indicator = None

        self.setup_ui()
        self.init_demo_data()

        # Timer để cập nhật vị trí của time indicator mỗi phút
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_indicator)
        self.timer.start(60000)  # Cập nhật mỗi phút (60000ms)

        # Khởi tạo time indicator
        self.update_time_indicator()

        # Timer cho đồng hồ
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Cập nhật mỗi giây
        self.update_clock()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Header layout chứa các tab và thanh công cụ
        self.header_layout = QHBoxLayout()

        # Các nút tab
        self.tab_layout = QHBoxLayout()
        self.tab_layout.setSpacing(0)

        self.tabs = ["Danh sách", "Hạn chót", "Trình lập kế hoạch", "Lịch", "Gantt"]
        self.tab_buttons = []

        for tab_text in self.tabs:
            btn = QPushButton(tab_text)
            btn.setCheckable(True)
            if tab_text == "Gantt":
                btn.setChecked(True)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E6E6E6;
                        border-top: 1px solid #CCCCCC;
                        border-left: 1px solid #CCCCCC;
                        border-right: 1px solid #CCCCCC;
                        border-bottom: none;
                        padding: 8px 16px;
                        font-weight: bold;
                        color: #333333;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        padding: 8px 16px;
                        color: #555555;
                    }
                    QPushButton:hover {
                        background-color: rgba(0, 0, 0, 0.05);
                    }
                """)
            self.tab_buttons.append(btn)
            self.tab_layout.addWidget(btn)

        self.tab_layout.addStretch()
        self.header_layout.addLayout(self.tab_layout)

        # Layout cho các tab "Các mục của tôi"
        self.my_items_layout = QHBoxLayout()
        self.my_items_label = QLabel("Các mục của tôi:")
        self.my_items_label.setStyleSheet("color: #555555; margin-right: 10px;")
        self.my_items_layout.addWidget(self.my_items_label)

        # Nút Quá hạn với badge
        self.overdue_btn = QPushButton("Quá hạn")
        self.overdue_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 8px 16px;
                padding-right: 30px;
                color: #555555;
                position: relative;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
        """)
        self.my_items_layout.addWidget(self.overdue_btn)

        # Badge cho nút Quá hạn
        self.overdue_badge = QLabel("1")
        self.overdue_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overdue_badge.setStyleSheet("""
            background-color: #FF0000;
            color: white;
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 10px;
        """)
        self.overdue_badge.setFixedSize(18, 18)

        # Thêm badge vào nút
        self.overdue_btn.setLayout(QHBoxLayout())
        self.overdue_btn.layout().addStretch()
        self.overdue_btn.layout().addWidget(self.overdue_badge)
        self.overdue_btn.layout().setContentsMargins(0, 0, 10, 0)

        # Nút Bình luận với badge
        self.comments_btn = QPushButton("Bình luận")
        self.comments_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 8px 16px;
                padding-right: 30px;
                color: #555555;
                position: relative;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
        """)
        self.my_items_layout.addWidget(self.comments_btn)

        # Badge cho nút Bình luận
        self.comments_badge = QLabel("0")
        self.comments_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.comments_badge.setStyleSheet("""
            background-color: #888888;
            color: white;
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 10px;
        """)
        self.comments_badge.setFixedSize(18, 18)

        # Thêm badge vào nút
        self.comments_btn.setLayout(QHBoxLayout())
        self.comments_btn.layout().addStretch()
        self.comments_btn.layout().addWidget(self.comments_badge)
        self.comments_btn.layout().setContentsMargins(0, 0, 10, 0)

        self.my_items_layout.addStretch()

        # Nút đánh dấu đọc tất cả
        self.mark_all_read_btn = QPushButton("Đánh dấu đã đọc tất cả")
        self.mark_all_read_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 8px 16px;
                color: #0066CC;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.my_items_layout.addWidget(self.mark_all_read_btn)

        self.header_layout.addLayout(self.my_items_layout)
        self.main_layout.addLayout(self.header_layout)

        # Separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator.setStyleSheet("background-color: #CCCCCC;")
        self.main_layout.addWidget(self.separator)

        # Scroll area cho biểu đồ Gantt
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("background-color: white;")

        # Widget chứa nội dung biểu đồ Gantt
        self.gantt_content = QWidget()
        self.gantt_layout = QVBoxLayout(self.gantt_content)
        self.gantt_layout.setContentsMargins(0, 0, 0, 0)
        self.gantt_layout.setSpacing(0)

        # Thêm đồng hồ
        self.clock_widget = QLabel()
        self.clock_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.clock_widget.setStyleSheet("""
            font-size: 14px;
            color: #333333;
            background-color: #F0F0F0;
            padding: 5px 15px;
            border-radius: 3px;
            margin: 10px;
        """)
        self.gantt_layout.addWidget(self.clock_widget, alignment=Qt.AlignmentFlag.AlignRight)

        # Widget cho Gantt chart (sẽ được vẽ bằng paintEvent)
        self.chart_widget = QWidget()
        self.chart_widget.setMinimumHeight(500)
        self.chart_widget.paintEvent = self.paint_gantt_chart
        self.gantt_layout.addWidget(self.chart_widget)

        # Thêm thanh trạng thái
        self.status_bar = QLabel("TRANG: 1")
        self.status_bar.setStyleSheet("color: #666666; padding: 5px;")
        self.gantt_layout.addWidget(self.status_bar)

        self.scroll_area.setWidget(self.gantt_content)
        self.main_layout.addWidget(self.scroll_area)

    def init_demo_data(self):
        # Khởi tạo dữ liệu demo
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.start_date = today - timedelta(days=3)

        self.tasks = [
            Task(1, "Tab Vụ", today - timedelta(days=2), today + timedelta(days=3), 70, "#FF6B6B"),
            Task(2, "Tạo Phần Mềm", today, today + timedelta(days=5), 30, "#4ECDC4")
        ]

    def paint_gantt_chart(self, event):
        painter = QPainter(self.chart_widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Lấy kích thước widget
        width = self.chart_widget.width()
        height = self.chart_widget.height()

        # Vẽ background
        painter.fillRect(0, 0, width, height, QColor("#FFFFFF"))

        # Vẽ header
        header_rect = QRect(0, 0, width, self.header_height)
        painter.fillRect(header_rect, QColor("#F5F5F5"))

        # Vẽ cột nhãn task
        label_rect = QRect(0, 0, self.label_width, height)
        painter.fillRect(label_rect, QColor("#F0F0F0"))

        # Vẽ đường phân cách giữa cột nhãn và biểu đồ
        painter.setPen(QPen(QColor("#CCCCCC"), 1))
        painter.drawLine(self.label_width, 0, self.label_width, height)

        # Vẽ header cho các ngày
        painter.setFont(QFont("Arial", 10))
        for i in range(self.days_to_show):
            date = self.start_date + timedelta(days=i)
            day_str = str(date.day)
            month_str = date.strftime("%m")

            x = self.label_width + i * self.cell_width

            # Highlight ngày hiện tại
            if date.date() == datetime.now().date():
                painter.fillRect(x, 0, self.cell_width, self.header_height, QColor("#E6F7FF"))

            # Vẽ số ngày
            painter.drawText(QRect(x, 5, self.cell_width, 20), Qt.AlignmentFlag.AlignCenter, day_str)

            # Vẽ đường phân cách giữa các ngày
            painter.drawLine(x, 0, x, height)

            # Vẽ tháng (chỉ vẽ 1 lần cho mỗi tháng)
            if i == 0 or date.day == 1:
                painter.drawText(QRect(x, 25, self.cell_width * 2, 20), Qt.AlignmentFlag.AlignLeft, month_str)

        # Vẽ đường phân cách header và nội dung
        painter.drawLine(0, self.header_height, width, self.header_height)

        # Vẽ các task
        for idx, task in enumerate(self.tasks):
            y = self.header_height + idx * self.row_height

            # Vẽ tên task trong cột nhãn
            task_name_rect = QRect(5, y, self.label_width - 10, self.row_height)
            painter.drawText(task_name_rect, Qt.AlignmentFlag.AlignVCenter, task.name)

            # Tính toán vị trí và độ dài của thanh task
            days_from_start = (task.start_date - self.start_date).days
            task_duration = (task.end_date - task.start_date).days + 1

            if days_from_start < 0:
                # Task bắt đầu trước ngày bắt đầu hiển thị
                task_duration += days_from_start  # Giảm độ dài hiển thị
                days_from_start = 0

            task_x = self.label_width + days_from_start * self.cell_width
            task_width = task_duration * self.cell_width

            # Vẽ thanh task
            task_rect = QRect(task_x, y + 5, task_width, self.row_height - 10)

            # Vẽ phần tiến độ hoàn thành
            if task.progress > 0:
                progress_width = int(task_width * task.progress / 100)
                progress_rect = QRect(task_x, y + 5, progress_width, self.row_height - 10)
                painter.fillRect(progress_rect, QColor(task.color))

                # Vẽ phần còn lại
                remaining_rect = QRect(task_x + progress_width, y + 5, task_width - progress_width, self.row_height - 10)
                painter.fillRect(remaining_rect, QColor(task.get_remaining_color()))
            else:
                painter.fillRect(task_rect, QColor(task.get_remaining_color()))

            # Vẽ viền cho thanh task
            painter.setPen(QPen(QColor("#999999"), 1))
            painter.drawRect(task_rect)

            # Vẽ phần trăm hoàn thành
            progress_text = f"{task.progress}%"
            painter.drawText(task_rect, Qt.AlignmentFlag.AlignCenter, progress_text)

            # Vẽ đường kẻ phân cách giữa các task
            painter.setPen(QPen(QColor("#EEEEEE"), 1))
            painter.drawLine(0, y + self.row_height, width, y + self.row_height)

        # Vẽ time indicator (đường kẻ đỏ chỉ thời gian hiện tại)
        current_time = datetime.now()
        days_passed = (current_time - self.start_date).total_seconds() / (24 * 3600)
        time_x = self.label_width + days_passed * self.cell_width

        if 0 <= time_x <= width:
            painter.setPen(QPen(QColor("#FF0000"), 2))
            painter.drawLine(int(time_x), self.header_height, int(time_x), height)

    def update_time_indicator(self):
        # Cập nhật vị trí của time indicator
        self.chart_widget.update()  # Yêu cầu vẽ lại chart để cập nhật vị trí đường kẻ thời gian

    def update_clock(self):
        # Cập nhật đồng hồ thời gian thực
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M:%S - %d/%m/%Y")
        self.clock_widget.setText(f"⏰ {time_str}")


class GanttChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biểu đồ Gantt Thời Gian Thực")
        self.setGeometry(100, 100, 1000, 600)

        # Widget chính
        self.central_widget = GanttChartView()
        self.setCentralWidget(self.central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GanttChartWindow()
    window.show()
    sys.exit(app.exec())