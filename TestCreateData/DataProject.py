import random
import json
from Models.Project import Project
from libs.JsonFileFactory import JsonFileFactory

# Load 100 users vào danh sách
with open('../Dataset/users.json', 'r', encoding='utf-8') as f:
    users = json.load(f)

user_emails = [user['Email'] for user in users]

# Danh sách tên project đa lĩnh vực
project_titles = [
    "Xây dựng website thương mại điện tử", "Ứng dụng đặt vé máy bay", "Hệ thống quản lý khách sạn",
    "Phần mềm kế toán doanh nghiệp", "App theo dõi sức khỏe", "Phần mềm quản lý trường học",
    "Ứng dụng mạng xã hội dành cho giới trẻ", "Nghiên cứu thị trường bất động sản",
    "Phát triển hệ thống AI Chatbot", "Dự án chuyển đổi số doanh nghiệp", "Ứng dụng học tiếng Anh",
    "Hệ thống đặt xe online", "Xây dựng sàn thương mại điện tử B2B", "Ứng dụng ngân hàng số",
    "Dự án ERP cho doanh nghiệp vừa và nhỏ", "Hệ thống điều khiển nhà thông minh (Smart Home)",
    "Ứng dụng quản lý quán cafe", "Phát triển phần mềm CRM", "Phần mềm tính lương và chấm công",
    "Hệ thống quản lý chuỗi cung ứng", "Dự án công nghệ Blockchain", "Xây dựng App thời trang",
    "Ứng dụng học lái xe mô phỏng", "Phát triển Game mobile phiêu lưu", "Dự án quản lý thư viện",
    "Hệ thống bán vé xem phim online", "Nâng cấp website chính phủ điện tử", "Hệ thống quản lý y tế",
    "Ứng dụng tuyển dụng trực tuyến", "Dự án camera AI nhận diện khuôn mặt", "Hệ thống logistics",
    "Ứng dụng chăm sóc thú cưng", "Phát triển phần mềm kế hoạch marketing", "Quản lý fanpage đa nền tảng",
    "Phần mềm học lập trình trực tuyến", "Ứng dụng du lịch khám phá địa phương", "Dự án phát triển AI dịch tự động",
    "Xây dựng ứng dụng giáo dục trẻ em", "App livestream bán hàng", "Dự án thanh toán không tiền mặt",
    "Quản lý giao hàng và đơn vận", "Xây dựng trang báo điện tử", "Ứng dụng đặt lịch khám bệnh",
    "Hệ thống quản lý bãi giữ xe", "Xây dựng App học guitar", "Dự án AI nhận diện giọng nói",
    "Ứng dụng đặt đồ ăn online", "Hệ thống kết nối nông sản sạch", "Phần mềm quản lý hồ sơ nhân sự",
    "Hệ thống đánh giá sản phẩm", "Ứng dụng học từ vựng Tiếng Anh", "Dự án nghiên cứu thị trường số",
    "Quản lý quỹ đầu tư chứng khoán", "Hệ thống quản lý trung tâm ngoại ngữ", "Ứng dụng kết nối Freelancer",
    "Xây dựng game nhập vai", "Ứng dụng đọc sách điện tử", "Hệ thống bảo mật website", "Phần mềm quản lý vận tải",
    "Ứng dụng thi thử online", "Hệ thống cảnh báo thiên tai", "Phát triển phần mềm kế hoạch tài chính",
    "Ứng dụng tư vấn tâm lý online", "Xây dựng sàn giao dịch tiền ảo", "Ứng dụng kết nối việc làm",
    "App học nhạc lý cơ bản", "Ứng dụng chăm sóc sắc đẹp", "Dự án Blockchain truy xuất nguồn gốc",
    "Quản lý điểm thi đại học", "Hệ thống cảnh báo an ninh", "Xây dựng mạng xã hội giáo dục",
    "App tính toán chi phí xây dựng", "Ứng dụng đặt tiệc sự kiện", "Dự án AI phân tích thị trường",
    "Ứng dụng luyện nói IELTS", "Hệ thống quản lý xưởng sản xuất", "App quản lý gia phả dòng họ",
    "Ứng dụng đặt homestay", "Phần mềm quản lý tiệm bánh", "App học tiếng Hàn", "Ứng dụng review phim",
    "Hệ thống kiểm soát ra vào", "App quản lý phòng Gym", "Ứng dụng đo chất lượng không khí",
    "Dự án giảng dạy trực tuyến", "Ứng dụng cảnh báo trộm", "Hệ thống quản lý Spa", "App thuê xe tự lái",
    "Hệ thống phân tích big data", "Ứng dụng săn sale online", "App học tiếng Nhật", "Ứng dụng quản lý quỹ từ thiện",
    "Dự án AI dự đoán chứng khoán", "Hệ thống đánh giá nhân sự", "Ứng dụng viết nhật ký",
    "App kết nối gia sư", "Ứng dụng theo dõi vận động", "App làm bài tập về nhà", "Hệ thống quản lý farmstay",
    "Ứng dụng học toán online", "Dự án chăm sóc người cao tuổi", "App hỗ trợ pháp lý"
]

projects = []
for i in range(100):
    project_id = f"PRJ{str(i + 1).zfill(3)}"
    name = project_titles[i]
    assignment = random.sample(user_emails, random.randint(1, 3))
    manager = random.choice(user_emails)
    status = random.choice(["Open", "Ongoing", "Pending", "Completed", "Canceled"])
    progress = random.randint(0, 100)
    start_date = f"{random.randint(1, 28)}/0{random.randint(1, 6)}/2025"
    end_date = f"{random.randint(1, 28)}/0{random.randint(7, 12)}/2025"
    priority = random.choice(["Priority 1", "Priority 2", "Priority 3", "Priority 4"])

    project = Project(
        project_id=project_id,
        name=name,
        assignment=assignment,
        manager=manager,
        status=status,
        progress=progress,
        start_date=start_date,
        end_date=end_date,
        color="#FF6B6B",
        priority=priority,
        description=f"{name} mô tả chi tiết dự án...",
        attachments=[],
        dependency="",
        estimated_time="4 weeks",
        view_gantt=True,
        view_kanban=True,
        drag_and_drop=True
    )
    projects.append(project)

# Xuất ra file JSON
jff = JsonFileFactory()
filename = "../Dataset/projects.json"
if jff.write_data(projects, filename):
    print(f"✅ Tạo thành công 100 Project vào {filename}")
else:
    print("❌ Lỗi khi ghi file project.json")
