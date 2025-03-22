import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCalendarWidget, QListWidget,
    QLineEdit, QPushButton, QLabel, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate


class ScheduleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schedule Tracker")
        self.resize(600, 500)

        # Dictionary to hold events: key=date string, value=list of events.
        self.events = {}

        # Main horizontal layout: Left for calendar, right for event list and controls
        main_layout = QHBoxLayout(self)

        # Left side layout for the calendar
        left_layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.load_events_for_date)
        left_layout.addWidget(self.calendar)
        main_layout.addLayout(left_layout)

        # Right side layout for events and controls
        right_layout = QVBoxLayout()
        # Label to display selected date
        self.label_selected_date = QLabel("Events for " + self.calendar.selectedDate().toString("yyyy-MM-dd"))
        right_layout.addWidget(self.label_selected_date, alignment=Qt.AlignmentFlag.AlignCenter)

        # List widget to display events
        self.list_events = QListWidget()
        right_layout.addWidget(self.list_events)

        # Horizontal layout for adding a new event
        add_layout = QHBoxLayout()
        self.lineedit_event = QLineEdit()
        self.lineedit_event.setPlaceholderText("Enter new event...")
        add_layout.addWidget(self.lineedit_event)
        self.btn_add_event = QPushButton("Add Event")
        self.btn_add_event.clicked.connect(self.add_event)
        add_layout.addWidget(self.btn_add_event)
        right_layout.addLayout(add_layout)

        # Button to remove selected event(s)
        self.btn_remove_event = QPushButton("Remove Selected Event")
        self.btn_remove_event.clicked.connect(self.remove_event)
        right_layout.addWidget(self.btn_remove_event)

        # Add stretch to push content up
        right_layout.addStretch()

        main_layout.addLayout(right_layout)

    def load_events_for_date(self):
        """Load and display events for the currently selected date."""
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString("yyyy-MM-dd")
        self.label_selected_date.setText("Events for " + date_str)
        self.list_events.clear()
        if date_str in self.events:
            for event in self.events[date_str]:
                self.list_events.addItem(event)

    def add_event(self):
        """Add an event for the selected date."""
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
        """Remove the selected event(s) from the list."""
        selected_items = self.list_events.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select an event to remove!")
            return
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString("yyyy-MM-dd")
        for item in selected_items:
            self.events[date_str].remove(item.text())
        self.load_events_for_date()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScheduleWidget()
    window.show()
    sys.exit(app.exec())
