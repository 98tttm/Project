from datetime import datetime

class Project:
    def __init__(
        self,
        project_id: str,
        name: str,
        assignment: list,
        manager: str,
        status: str,
        progress: int,
        start_date: str,
        end_date: str,
        color="#FF6B6B",
        priority : str ="Normal",
        description: str ="",
        attachments: list =None,
        dependency: str ="",
        estimated_time="",
        view_gantt=False,
        view_kanban=False,
        drag_and_drop=False
    ):
        self.project_id = project_id
        self.name = name
        self.assignment = assignment if assignment else []
        self.manager = manager
        self.status = status
        self.progress = progress
        self.start_date = start_date
        self.end_date = end_date
        self.color = color
        self.priority = priority
        self.description = description
        self.attachments = attachments if attachments else []
        self.dependency = dependency
        self.estimated_time = estimated_time
        self.view_gantt = view_gantt
        self.view_kanban = view_kanban
        self.drag_and_drop = drag_and_drop

    def __str__(self):
        return (
            f"ProjectID: {self.project_id} | Name: {self.name} | "
            f"Assignment: {self.assignment} | Manager: {self.manager} | "
            f"Status: {self.status} | Progress: {self.progress}% | "
            f"Start: {self.start_date} | End: {self.end_date} | "
            f"Priority: {self.priority} | Dependency: {self.dependency} | "
            f"EstimatedTime: {self.estimated_time} | "
            f"Gantt?: {self.view_gantt}, Kanban?: {self.view_kanban}, "
            f"DragDrop?: {self.drag_and_drop}"
        )

    def parse_date(self, date_str: str) -> datetime:
        """
        Attempt to parse a date string using multiple common formats.
        Fallback to the current date if parsing fails.
        """
        formats = ["%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        # Fallback
        print(f"Failed to parse date: '{date_str}'. Using current date/time.")
        return datetime.now()
