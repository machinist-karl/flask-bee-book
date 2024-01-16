from datetime import datetime, timedelta
from math import floor

from flask import current_app
from sqlalchemy import Column, Integer, String, Boolean, Float
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.jose import jwt

from app.libs.enums import ApplyStatus
from app.libs.helper import is_isbn_or_key
from app.models.base import Base, db
from flask_login import UserMixin
from app import login_manager
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.wish import Wish
from app.spider.bee_book import BeeBook

"""
    UserMixin:
        从该类中继承get_id()等方法，方便将user id塞入用户cookie中
"""


class User(UserMixin, Base):
    """
        默认情况下sqlalchemy会将类名作为表名
        如果不希望使用默认表名，可以进行如下设置
        __tablename__ = "userinfo"
    """
    id = Column(Integer, primary_key=True)  # primary
    nickname = Column(String(24), nullable=False)  # 用户昵称
    phone_number = Column(String(18), unique=True)  # 用户手机号
    _password = Column('password', String(256), nullable=False)  # 用户登录密码
    email = Column(String(50), unique=True, nullable=False)  # 用户邮箱
    confirmed = Column(Boolean, default=False)  # 用户
    beans = Column(Float, default=0)  # 用户积分
    send_counter = Column(Integer, default=0)
    receive_counter = Column(Integer, default=0)
    wx_open_id = Column(String(50))  # 供后期微信小程序使用,暂不使用
    wx_name = Column(String(32))  # 供后期微信小程序使用,暂不使用

    # 设置password的setter和getter方法
    # 注意: 函数名称password要与request中的参数名称相同
    # 否则无法调用setter方法进行属性赋值
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password: str):
        # 对用户原始密码进行加密
        self._password = generate_password_hash(raw_password)

    def can_send_drift(self):
        """
           业务规则一:
            申请人的积分不能小于1
        """
        if self.beans < 1:
            return False

        """
           业务规则二:
            申请人每得到2本书,必须成功赠送1本书
        """
        # 申请人已成功赠送书的数量
        success_donated_books_count = Gift.query.filter_by(
            uid=self.id, launched=True).count()
        # 申请人已成功获取书的数量
        """
            pending=ApplyStatus.SUCCESS, 将调用drift模型中的方法
            进行转换将枚举转换成DB中的数字型
            @pending.setter
            def pending(self, status):
                self._pending = status.value
        """
        apply_success_books_count = Drift.query.filter_by(
            requester_id=self.id, pending=ApplyStatus.SUCCESS
        ).count()

        return True if floor(apply_success_books_count / 2) <= \
                       floor(success_donated_books_count) else False

    def check_password(self, raw_password: str):
        return check_password_hash(self._password, raw_password)

    # 根据用户id生成用户token
    def generate_token(self, expiration=600):
        header = {'alg': current_app.config['TOKEN_ALGORITHM']}
        key = current_app.config['SECRET_KEY']
        expiration_time = datetime.utcnow() + timedelta(seconds=expiration)
        # exp为jwt默认的失效时间参数名称,不要修改为其它名称
        payload = {'id': self.id, 'exp': expiration_time}
        temp_id_token = jwt.encode(header, payload, key=key).decode('utf-8')

        return temp_id_token

    # 赠送者的简要信息，该信息用于书籍申请页面
    @property
    def summary(self):
        return dict(
            nickname=self.nickname,
            beans=self.beans,
            email=self.email,
            send_receive=str(self.send_counter) + '/' + str(self.receive_counter)
        )

    @staticmethod
    def reset_password(token, new_password: str):
        key = current_app.config['SECRET_KEY']
        try:
            raw = jwt.decode(token, key)
        except:
            return False
        uid = raw['id']
        if not uid:
            return False

        with db.auto_commit():
            user: User = User.query.get(uid)
            # 直接更新对象的属性值,即可触发update操作
            user.password = new_password

        return True

    # 判断ISBN号是否存在并且合法
    def can_save_to_list(self, isbn: str) -> bool:
        # 1) 校验isbn是否合法
        if is_isbn_or_key(isbn) != 'isbn':
            return False

        # 2) 校验isbn是否存在
        bee_book = BeeBook()
        bee_book.search_by_isbn(isbn)
        # 自定义first属性,返回对象books列表中的第一个元素
        if not bee_book.first:
            return False

        # 3) 对于单个用户不能同时赠送多本相同的图书
        # 用户不能把多本相同的书放入到待赠送清单中

        my_gifts = Gift.query.filter_by(uid=self.id, isbn=isbn,
                                        launched=False).first()

        # 4) 对于图书的所有者，其不能获得自己赠送的书
        my_wishes = Wish.query.filter_by(uid=self.id, isbn=isbn,
                                         launched=False).first()

        # 如果这本书不在待赠送清单中且又不在自己的心愿清单中,才能加入本书到wish清单中
        if not my_gifts and not my_wishes:
            return True
        else:
            return False


"""
    1. 需要提供callback函数给login_manager
    2. user_loader由login_manager提供, 返回一个str类型的user_id
    3. @login_required装饰器需要调用该函数
    4. 该函数需要单独的定义在外部,而不是User的内部
    5. 该函数不仅能返回一个User的id值供cookie使用，同时也会生成一个用户的实例对象
    供flask_login中的current_user使用
"""


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
