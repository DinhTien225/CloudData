import enum
import json
import math

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Time, Boolean, event, update

from CloudDataStorage.Cloud import db, app


class User(db.Model,UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)

    def __str__(self):
        return f"{self.name} - {self.role.value}"

# Tạo cơ sở dữ liệu và thêm sân bay mặc định
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        import hashlib

        password = str(hashlib.md5("123".encode('utf-8')).hexdigest())
        u = User(name="abc", email="abc@gmail.com", password=password)
        db.session.add(u)

        db.session.commit()