import os
from datetime import datetime

from Models.Notification import Notification
from Models.User import User
from Models.Project import Project
from libs.JsonFileFactory import JsonFileFactory
from libs.DataConnector import DataConnector

# --- Sử dụng DataConnector để lấy dữ liệu đã có ---
dc = DataConnector()

# Lấy danh sách user và project từ dataset
users = dc.get_all_users()  # Trả về list các User (nếu có)
projects = dc.get_all_projects()  # Trả về list các Project (nếu có)

# Kiểm tra dữ liệu có hợp lệ không
if not users:
    print("Không tìm thấy user nào trong dataset!")
    exit(1)
if not projects:
    print("Không tìm thấy project nào trong dataset!")
    exit(1)

# Ví dụ: sử dụng user đầu tiên và 2 project đầu tiên (nếu có)
user1 = users[0]
if len(projects) >= 2:
    project1 = projects[0]
    project2 = projects[1]
else:
    # Nếu chỉ có 1 project thì dùng nó cho tất cả các notification mẫu
    project1 = projects[0]
    project2 = projects[0]

# Lấy thời gian hiện tại
now_str = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

# Tạo danh sách notification sử dụng dữ liệu từ dataset
notifications = [
    Notification(username=user1, action="added", project_id=project1, time_str=now_str),
    Notification(username=user1, action="updated", project_id=project2, time_str=now_str),
    Notification(username=user1, action="deleted", project_id=project2, time_str=now_str)
]

# --- Chuyển đổi danh sách notifications thành list các dict chỉ chứa các key cần thiết ---
lite_list = []
for noti in notifications:
    lite_list.append({
        "username": noti.username.Username if noti.username else "",
        "action": noti.action,
        "project_id": noti.project_id.project_id if noti.project_id else "",
        "time_str": noti.time_str
    })

# --- Ghi dữ liệu notifications ra file JSON ---
jff = JsonFileFactory()
# Xây dựng đường dẫn tuyệt đối đến notifications.json (dùng thư mục Dataset trong project)
base_dir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(base_dir, "..", "Dataset", "notifications.json")
success = jff.write_data(lite_list, filename)

if success:
    print(f"Notifications successfully written to {filename}")
else:
    print("Failed to write notifications data.")
