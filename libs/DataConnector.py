import hashlib
import os

from Models.Project import Project
from Models.User import User
from libs.JsonFileFactory import JsonFileFactory


class DataConnector:
    """
    DataConnector provides methods to read and write project, user, and notification data
    from JSON files using the JsonFileFactory.
    """

    def __init__(self):
        # Build an absolute path to the JSON data files
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.projects_file = os.path.join(base_dir, "..", "Dataset", "projects.json")
        self.users_file = os.path.join(base_dir, "..", "Dataset", "users.json")
        # Đường dẫn cho notifications.json
        self.notifications_file = os.path.join(base_dir, "..", "Dataset", "notifications.json")

    def get_all_projects(self):
        """
        Returns a list of Project objects loaded from the projects JSON file.
        """
        print("Projects file path:", self.projects_file)
        if not os.path.exists(self.projects_file):
            print("File not found:", self.projects_file)
            return []
        jff = JsonFileFactory()
        projects = jff.read_data(self.projects_file, Project)
        print("Loaded projects:", projects)  # Debug
        return projects if projects is not None else []

    def get_all_users(self):
        """
        Returns a list of User objects loaded from the users JSON file.
        """
        if not os.path.exists(self.users_file):
            print("File not found:", self.users_file)
            return []
        jff = JsonFileFactory()
        return jff.read_data(self.users_file, User) or []

    def get_user_by_username(self, username):
        """
        Returns a User object matching the given username, or None if not found.
        """
        users = self.get_all_users()
        for user in users:
            if user.Username == username:
                return user
        return None

    def get_project_by_projectid(self, project_id):
        """
        Returns a Project object matching the given project_id (compared as string),
        or None if not found.
        """
        projects = self.get_all_projects()
        for project in projects:
            if str(project.project_id) == str(project_id):
                return project
        return None

    def add_project(self, project):
        """
        Adds a new project to the projects JSON file.
        """
        projects = self.get_all_projects()
        projects.append(project)
        jff = JsonFileFactory()
        jff.write_data(projects, self.projects_file)

    def add_user(self, user):
        """
        Adds a new user to the users JSON file. The user's password is hashed
        before saving.
        """
        user.Password = hashlib.sha256(user.Password.encode()).hexdigest()
        users = self.get_all_users()
        users.append(user)
        jff = JsonFileFactory()
        jff.write_data(users, self.users_file)

    def save_project(self, project):
        """
        Updates an existing project with the same project_id or adds it if it doesn't exist,
        then writes the full list to the projects JSON file.
        """
        projects = self.get_all_projects()
        for i, p in enumerate(projects):
            if p.project_id == project.project_id:
                projects[i] = project
                break
        else:
            projects.append(project)
        self.write_projects_to_file(projects)

    def save_all_projects(self, projects):
        """
        Saves the given list of Project objects to the projects JSON file.
        """
        self.write_projects_to_file(projects)

    def write_projects_to_file(self, projects):
        """
        Writes the list of Project objects to the projects JSON file using JsonFileFactory.
        """
        jff = JsonFileFactory()
        jff.write_data(projects, self.projects_file)

    def login(self, username, password):
        """
        Checks the provided credentials and returns the corresponding User object if valid,
        or None otherwise.
        """
        hashed_input = hashlib.sha256(password.encode()).hexdigest()
        users = self.get_all_users()
        for user in users:
            if user.Username == username and user.Password == hashed_input:
                return user
        return None

    def update_password(self, email, new_password):
        """
        Updates the password for the user with the specified email. The password is hashed
        before saving. Returns True if successful, otherwise False.
        """
        email_normalized = email.strip().lower()
        users = self.get_all_users()
        updated = False

        for user in users:
            print(f"Checking user: {user.Username} (or {user.Email})")
            if user.Email.strip().lower() == email_normalized:
                user.Password = hashlib.sha256(new_password.encode()).hexdigest()
                updated = True
                print(f"Password updated for user: {user.Username}")
                break

        if updated:
            jff = JsonFileFactory()
            jff.write_data(users, self.users_file)
            return True
        else:
            print("No matching user found for email:", email)
            return False

    def save_notifications(self, notifications):
        """
        Saves the list of notification dicts to the notifications JSON file.
        Each dict should contain:
          {
            "username": ...,
            "action": ...,
            "project_id": ...,
            "time_str": ...
          }
        """
        jff = JsonFileFactory()
        return jff.write_data(notifications, self.notifications_file)

    def load_notifications(self):
        """
        Loads the list of notification dicts from the notifications JSON file.
        Returns a list of dicts.
        """
        if not os.path.exists(self.notifications_file):
            return []
        jff = JsonFileFactory()
        data = jff.read_data(self.notifications_file, dict)  # đọc file chứa list of dict
        return data if data is not None else []
