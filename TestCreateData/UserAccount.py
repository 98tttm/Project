import hashlib
import random

from Models.User import User
from libs.JsonFileFactory import JsonFileFactory

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create sample users.
# For some users, an avatar image file path is provided.
# For others, the default avatar (e.g. "default_avatar.png") will be used.
users = []
users.append(User(
    "Trần Thanh Thịnh",
    "thinhtt234111e@st.uel.edu.vn",
    "0987655755",
    "min5a1ak9999",
    hash_password("ThinhTran09082005@"),
    "D:\PHẦN MỀM QUẢN LÝ DỰ ÁN_FINALPROJECT\Image\z5952311538473_ea6978a9529ba82f5a3f7a9a13b9c7de.jpg"  # Update path as needed
))
users.append(User(
    "Nguyễn Thế Thông",
    "thongnt234111e@st.uel.edu.vn",
    "0976543210",
    "thongnt234111e@st.uel.edu.vn",
    hash_password("123"),
    "avatars/thong.png"  # Update path as needed
))
users.append(User(
    "Huỳnh Tấn Phát",
    "phatht234111e@st.uel.edu.vn",
    "0922042005",
    "phatht234111e@st.uel.edu.vn",
    hash_password("123")
    # No avatar provided, so default will be used.
))
users.append(User(
    "Trịnh Thanh An",
    "antt234111e@st.uel.vn",
    "0954321098",
    "antt234111e@st.uel.vn",
    hash_password("123")
    # No avatar provided.
))
users.append(User(
    "Đỗ Thị Diễm Hương",
    "huongdtd234111e@st.uel.vn",
    "0943210987",
    "huongdtd234111e@st.uel.vn",
    hash_password("123"),
    "avatars/diem_huong.png"  # Update path as needed
))
for i in range(1, 101):
    full_name = f"Người Dùng {i}"
    email = f"user{i}@st.uel.vn"
    phone = f"09{random.randint(10000000,99999999)}"
    username = email
    password = hash_password(f"password{i}")
    avatar = f"avatars/user{i}.png"
    users.append(User(full_name, email, phone, username, password, avatar))

print("Danh sách tài khoản:")
for u in users:
    print(u)

# Save the users to a JSON file.
jff = JsonFileFactory()
filename = "../Dataset/users.json"  # Update the path as necessary
jff.write_data(users, filename)
