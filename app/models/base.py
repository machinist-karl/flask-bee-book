from contextlib import contextmanager
from flask_sqlalchemy.query import Query as _Query
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from sqlalchemy import Column, Integer, SmallInteger
from datetime import datetime


# 将原先的SQLAlchemy起别名并自定义一个同名的SQLAlchemy
# 同时自定义的SQLAlchemy继承flask_sqlalchemy中的SQLAlchemy
class SQLAlchemy(_SQLAlchemy):
    """
        自定义上下文管理器(面向切面编程) :
        无需在类中手工添加__enter()__与__exit()__
    """

    @contextmanager
    def auto_commit(self, **kwargs):
        try:
            yield
            self.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


# 覆盖框架中的方法,只查询状态有效的记录
class Query(_Query):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs['status'] = 1
        return super(Query, self).filter_by(**kwargs)


# flask封装的类需要从flask_sqlalchemy中导入
# 使用自定义的Query方法
db = SQLAlchemy(query_class=Query)


class Base(db.Model):
    # 通知框架无需创建db数据库,否则会先创建名为db库后再创建表
    __abstract__ = True
    create_time = Column('create_time', Integer)
    # 记录删除标志位
    status = Column(SmallInteger, default=1)

    def __init__(self):
        """
            datetime.now()
            --> datetime.datetime(2020, 12, 25, 15, 29, 32, 594303)
            datetime.now().timestamp()
            --> 1703489459.721017
        """
        self.create_time = int(datetime.now().timestamp())

    # 将form表单中的数据填入到model(bean)中
    def set_attrs(self, attrs: dict):
        for k, v in attrs.items():
            if hasattr(self, k) and k != 'id':
                setattr(self, k, v)

    @property
    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)
        else:
            return None

    # 将记录删除标志位置为已删除
    def delete(self):
        self.status = 0
