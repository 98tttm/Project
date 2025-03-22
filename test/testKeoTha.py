import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor


class ProjectItem(QListWidgetItem):
    def __init__(self, project_id, name, status):
        # Tạo văn bản hiển thị với tên và trạng thái
        display_text = f"{name}\n[Trạng thái: {status}]"
        super().__init__(display_text)

        # Lưu trữ thông tin dự án
        self.project_id = project_id
        self.project_name = name
        self.project_status = status

        # Thiết lập dữ liệu cho item
        self.setData(Qt.ItemDataRole.UserRole, project_id)
        self.setData(Qt.ItemDataRole.UserRole + 1, status)

        # Style cho item
        self.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setSizeHint(self.sizeHint().expandedTo(QSize(100, 60)))  # Đảm bảo kích thước vừa đủ

    def update_status(self, new_status):
        """Cập nhật trạng thái và hiển thị"""
        self.project_status = new_status
        self.setData(Qt.ItemDataRole.UserRole + 1, new_status)
        self.setText(f"{self.project_name}\n[Trạng thái: {new_status}]")


class ProjectListWidget(QListWidget):
    def __init__(self, status, update_callback, parent=None):
        super().__init__(parent)
        self.status = status
        self.update_callback = update_callback
        self.setStyleSheet("QListWidget { background-color: #f0f0f0; border-radius: 5px; }")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        # InternalMove allows dragging items between list widgets
        self.setDragDropMode(QListWidget.DragDropMode.DragDrop)  # Thay đổi từ InternalMove sang DragDrop
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
            # Nếu kéo thả trong cùng một danh sách
            super().dropEvent(event)
        else:
            # Nếu kéo từ danh sách khác
            item_data = event.mimeData()
            if not item_data.hasFormat("application/x-qabstractitemmodeldatalist"):
                event.ignore()
                return

            # Lấy vị trí thả
            drop_index = self.indexAt(event.position().toPoint())

            # Lấy item được kéo từ widget nguồn
            if source and source.currentItem():
                source_item = source.currentItem()
                project_id = source_item.data(Qt.ItemDataRole.UserRole)
                project_name = source_item.project_name

                # Tạo item mới với trạng thái mới
                new_item = ProjectItem(project_id, project_name, self.status)

                # Thêm item mới vào danh sách hiện tại
                if drop_index.isValid():
                    self.insertItem(drop_index.row(), new_item)
                else:
                    self.addItem(new_item)

                # Xóa item từ danh sách nguồn
                source.takeItem(source.row(source_item))

                # Cập nhật dữ liệu
                self.update_callback()

            event.acceptProposedAction()

    def addProjectItem(self, project_id, name, status):
        """Thêm item dự án với định dạng mới"""
        item = ProjectItem(project_id, name, status)
        self.addItem(item)
        return item


class KanbanBoard(QWidget):
    def __init__(self, projects):
        """
        :param projects: a list of dicts with:
          "id": unique ID,
          "name": project/task name,
          "status": must match one of self.statuses
        """
        super().__init__()
        self.setWindowTitle("Kanban Board")
        self.resize(1000, 600)
        self.setStyleSheet("background-color: #e6e6e6;")

        self.projects = projects
        # Example statuses for columns
        self.statuses = ["Open", "Pending", "Ongoing", "Completed", "Canceled"]
        self.status_colors = {
            "Open": "#c6e5ff",  # Light blue
            "Pending": "#ffffcc",  # Light yellow
            "Ongoing": "#d9f2d9",  # Light green
            "Completed": "#ccffcc",  # Lighter green
            "Canceled": "#ffcccc"  # Light red
        }

        # Main layout horizontally: each column is a vertical layout
        main_layout = QHBoxLayout(self)
        self.columns = {}

        for status in self.statuses:
            col_layout = QVBoxLayout()

            # Container frame for styling
            frame = QFrame()
            frame.setStyleSheet(f"background-color: {self.status_colors.get(status, '#ffffff')};")
            frame.setFrameShape(QFrame.Shape.Box)
            frame_layout = QVBoxLayout(frame)

            # Column label
            lbl = QLabel(status)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            lbl.setStyleSheet("padding: 5px;")
            frame_layout.addWidget(lbl)

            # Create the list widget
            lw = ProjectListWidget(status, update_callback=self.update_data)
            self.columns[status] = lw
            frame_layout.addWidget(lw)

            col_layout.addWidget(frame)
            main_layout.addLayout(col_layout)

        self.load_projects()

    def load_projects(self):
        """Populate columns with items from self.projects based on status."""
        for lw in self.columns.values():
            lw.clear()

        for p in self.projects:
            st = p.get("status", "Open")
            lw = self.columns.get(st)
            if lw is not None:
                lw.addProjectItem(p["id"], p["name"], st)

    def update_data(self):
        """Update self.projects to reflect new statuses after drag-drop."""
        # Tạo bản đồ trạng thái mới dựa trên vị trí hiện tại của các item
        updated_projects = []

        for status, lw in self.columns.items():
            for i in range(lw.count()):
                item = lw.item(i)
                proj_id = item.data(Qt.ItemDataRole.UserRole)

                # Tìm dự án tương ứng trong dữ liệu gốc
                for proj in self.projects:
                    if proj["id"] == proj_id:
                        # Cập nhật trạng thái của dự án
                        updated_proj = proj.copy()
                        updated_proj["status"] = status
                        updated_projects.append(updated_proj)
                        break

        # Cập nhật self.projects với dữ liệu mới
        self.projects = updated_projects

        # Debug: Print updated data
        print("Updated projects:")
        for p in self.projects:
            print(p)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Thiết lập style cho toàn bộ ứng dụng
    app.setStyle("Fusion")

    # Sample data with matching statuses
    projects = [
        {"id": 1, "name": "Task A", "status": "Open"},
        {"id": 2, "name": "Task B", "status": "Pending"},
        {"id": 3, "name": "Task C", "status": "Ongoing"},
        {"id": 4, "name": "Task D", "status": "Completed"},
        {"id": 5, "name": "Task E", "status": "Canceled"}
    ]

    window = KanbanBoard(projects)
    window.show()
    sys.exit(app.exec())