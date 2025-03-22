import sys
from collections import Counter
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QLineSeries, QValueAxis
from PyQt6.QtCore import Qt, QDate

# Dummy data: list of project dictionaries.
# Each project has a "status" and a "start_date" (in "yyyy-MM-dd" format).
dummy_projects = [
    {"status": "Open", "start_date": "2025-03-10"},
    {"status": "Pending", "start_date": "2025-03-11"},
    {"status": "Ongoing", "start_date": "2025-03-11"},
    {"status": "Completed", "start_date": "2025-03-12"},
    {"status": "Canceled", "start_date": "2025-03-13"},
    {"status": "Open", "start_date": "2025-03-14"},
    {"status": "Ongoing", "start_date": "2025-03-14"},
    {"status": "Open", "start_date": "2025-03-15"},
    {"status": "Completed", "start_date": "2025-03-15"},
    {"status": "Pending", "start_date": "2025-03-15"},
    {"status": "Open", "start_date": "2025-03-16"},
    {"status": "Completed", "start_date": "2025-03-16"},
    # Add more projects as needed...
]


class ChartWidget(QWidget):
    def __init__(self, projects, parent=None):
        super().__init__(parent)
        self.projects = projects

        self.setWindowTitle("Project Dashboard")
        self.resize(800, 600)

        # Main layout: vertical, with pie chart on top and line chart below.
        layout = QVBoxLayout(self)

        # Pie chart view to display project status distribution.
        self.pie_chart_view = QChartView()
        layout.addWidget(self.pie_chart_view)

        # Line chart view to display projects per week.
        self.line_chart_view = QChartView()
        layout.addWidget(self.line_chart_view)

        # Button to refresh charts (simulate data update)
        self.btn_refresh = QPushButton("Refresh Charts")
        self.btn_refresh.clicked.connect(self.update_charts)
        layout.addWidget(self.btn_refresh)

        # Optional spacer at the bottom
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Initially update charts
        self.update_charts()

    def update_charts(self):
        self.update_pie_chart()
        self.update_line_chart()

    def update_pie_chart(self):
        # Count projects by status.
        statuses = [p["status"] for p in self.projects]
        counts = Counter(statuses)
        # Ensure consistent order
        status_order = ["Open", "Pending", "Ongoing", "Completed", "Canceled"]
        series = QPieSeries()
        for status in status_order:
            count = counts.get(status, 0)
            if count > 0:
                series.append(f"{status} ({count})", count)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Project Distribution by Status")
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.pie_chart_view.setChart(chart)

    def update_line_chart(self):
        # Group projects by week number based on their start_date.
        week_counts = {}
        for p in self.projects:
            date = QDate.fromString(p["start_date"], "yyyy-MM-dd")
            if date.isValid():
                # QDate.weekNumber() returns a tuple: (week, year)
                week = date.weekNumber()[0]
                week_counts[week] = week_counts.get(week, 0) + 1

        series = QLineSeries()
        for week, count in sorted(week_counts.items()):
            series.append(week, count)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Number of Projects by Week")
        chart.createDefaultAxes()

        # Configure X-axis (week number)
        axisX = chart.axes(Qt.Orientation.Horizontal)[0]
        axisX.setTitleText("Week Number")
        # Configure Y-axis (project count)
        axisY = chart.axes(Qt.Orientation.Vertical)[0]
        axisY.setTitleText("Project Count")

        self.line_chart_view.setChart(chart)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChartWidget(dummy_projects)
    window.show()
    sys.exit(app.exec())
