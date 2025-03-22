"""Lỗi - Rejected File"""
import mysql.connector

class MySQLConnector:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="procheck_db"
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def fetch_all_projects(self):
        self.cursor.execute("SELECT * FROM projects")
        return self.cursor.fetchall()

    def insert_project(self, project_data):
        sql = """
        INSERT INTO projects (project_id, name, assignment, manager, status, progress, 
        start_date, end_date, priority, dependency, description, attachments)
        VALUES (%(project_id)s, %(name)s, %(assignment)s, %(manager)s, %(status)s, 
        %(progress)s, %(start_date)s, %(end_date)s, %(priority)s, %(dependency)s, 
        %(description)s, %(attachments)s)
        """
        self.cursor.execute(sql, project_data)
        self.conn.commit()

    def delete_project(self, project_id):
        sql = "DELETE FROM projects WHERE project_id = %s"
        self.cursor.execute(sql, (project_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
