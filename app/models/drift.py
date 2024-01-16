from sqlalchemy import Column, String, Integer, ForeignKey, SmallInteger

from app.libs.enums import ApplyStatus
from app.models.base import Base

"""
    书籍流转订单信息
"""


class Drift(Base):
    # 配置db中的表名
    __tablename__ = 'drift'

    id = Column(Integer, primary_key=True)
    # 申请人的真实姓名,页面上手工填写
    recipient_name = Column(String(20), nullable=False)
    # 申请人的姓名的地址,页面上手工填写
    address = Column(String(100), nullable=False)
    # 申请人给赠送者的留言,页面上手工填写
    message = Column(String(200))
    # 申请人的手机号,页面上手工填写
    mobile = Column(String(20), nullable=False)

    # 书籍信息
    isbn = Column(String(13))
    book_title = Column(String(50))
    book_author = Column(String(30))
    book_img = Column(String(350))

    # 申请人的信息
    requester_id = Column(Integer)  # DB中获取的申请人ID
    requester_nickname = Column(String(20))  # DB中获取的申请人的昵称

    # 赠送者信息
    gifter_id = Column(Integer)
    gift_id = Column(Integer)
    gifter_nickname = Column(String(20))

    # 申请订单的状态信息, 状态的定义见ApplyStatus枚举类
    # db中字段的名称为pending
    _pending = Column('pending', SmallInteger, default=1)

    # 共美剧类型与db中的pending字段(整数类型)之间进行转换
    @property
    def pending(self):
        return ApplyStatus(self._pending)

    @pending.setter
    def pending(self, status):
        self._pending = status.value