# 基础类型使用sqlalchemy导入
from sqlalchemy import Column, Integer, String
from app.models.base import db


class Book(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)  # 书名
    author = Column(String(30), default="未名")  # 作者
    binding = Column(String(20))  # 装订类型, 平装/精装
    publisher = Column(String(50))  # 出版社
    price = Column(String(20))  # 价格
    pages = Column(Integer)  # 页数
    pubdate = Column(String(20))  # 出版日期
    isbn = Column(String(15), nullable=False, unique=True)
    summary = Column(String(1000))
    image = Column(String(50))
