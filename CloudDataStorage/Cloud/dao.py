import hashlib
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from CloudDataStorage.Cloud import app, db
from CloudDataStorage.Cloud.models import User


def auth_user(email, password):
    with app.app_context():  # Đảm bảo chạy trong app context
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        user = User.query.filter(User.email == email.strip(), User.password == password).first()
        return user

def get_user_by_id(user_id):
    return User.query.get(user_id)

def add_user(name, email, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, email=email, password=password)
    db.session.add(u)
    db.session.commit()

def check_email_exists(email):
    return User.query.filter_by(email=email).first() is not None
#ZALO PAY
import hashlib
import hmac
import time
import requests

def  generate_apptransid():
    app_time = str(int(time.time() * 1000))
    app_trans_id = f'220817_{app_time}'
    return app_trans_id

class ZaloPayDAO:
    def __init__(self):
        self.app_id = '2553'  # ID của ứng dụng ZaloPay
        self.key1 = 'PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL'  # Khóa bí mật của ứng dụng
        self.callback_url = 'http://127.0.0.1:5000/callback'  # URL callback
        self.bank_code = 'zalopayapp'  # Mã ngân hàng (ZaloPay App)

    def create_order(self, amount, redirect_url, app_trans_id=None):
        # Dữ liệu đơn hàng
        app_user = 'ZaloPayDemo'  # Tên người dùng ứng dụng
        app_time = str(int(time.time() * 1000))  # Thời gian hiện tại
        app_trans_id =app_trans_id # ID giao dịch duy nhất
        embed_data = json.dumps({'redirecturl': redirect_url})
        item = '[]'  # Danh sách các sản phẩm (ở đây là chuỗi rỗng)
        description = f'ZaloPayDemo - Thanh toán cho đơn hàng #{app_trans_id}'

        # Cấu trúc dữ liệu gửi đến ZaloPay
        data = f"{self.app_id}|{app_trans_id}|{app_user}|{amount}|{app_time}|{embed_data}|{item}"
        mac = hmac.new(self.key1.encode(), data.encode(), hashlib.sha256).hexdigest()  # Tính toán mã xác thực

        # Thông tin yêu cầu gửi đến API ZaloPay
        params = {
            "app_id": self.app_id,
            "app_user": app_user,
            "app_time": app_time,
            "amount": amount,
            "app_trans_id": app_trans_id,
            "bank_code": self.bank_code,
            "embed_data": embed_data,
            "item": item,
            "callback_url": self.callback_url,
            "description": description,
            "mac": mac  # Mã xác thực
        }

        # Gửi yêu cầu đến API ZaloPay
        try:
            response = requests.post("https://sb-openapi.zalopay.vn/v2/create", data=params)
            response.raise_for_status()  # Kiểm tra mã trạng thái HTTP

            result = response.json()

            # In ra toàn bộ phản hồi để xem chi tiết
            print("ZaloPay Response:", result)

            # Kiểm tra nếu trả về thành công và có khóa order_url
            if result.get("return_code") == 1 and "order_url" in result:
                return result["order_url"]  # Trả về URL thanh toán
            else:
                return f"Error: {result.get('return_message', 'No return message')}"
        except requests.exceptions.RequestException as e:
            return f"Error in request to ZaloPay API: {str(e)}"
        except ValueError:
            return "Error: Invalid JSON response from ZaloPay"