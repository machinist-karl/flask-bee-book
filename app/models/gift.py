from sqlalchemy import Column, Integer, Boolean, ForeignKey, String, desc, func
from sqlalchemy.orm import relationship
from flask import current_app
from app.models.base import Base, db
from app.spider.bee_book import BeeBook


class Gift(Base):
    id = Column(Integer, primary_key=True)
    # 使用relationship()标识User模型与Gift模型之间的关系
    # 同时这个user也将被实例化
    user = relationship('User')
    # user.id中的user取是user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'))
    # 使用isbn号与Book模型关联
    isbn = Column(String(15), nullable=False)
    launched = Column(Boolean, default=False)  # 标记该本书籍是否已赠送

    def is_yourself_gift(self, uid):
        return True if self.uid == uid else False

    # 根据用户id号查询出该用户的所有未送出的礼物
    @classmethod
    def get_user_gifts(cls, uid):
        gifts = Gift.query.filter_by(uid=uid, launched=False).order_by(desc(Gift.create_time)).all()

        return gifts

    # 给定一个分组,查询每本书有几个人加入到了心愿单中
    # 使用filter方法而不是filter_by()
    """
        # select count(id), isbn from wish 
        where launched=1 and status = 1
        and isbn in (select isbn from gift)
        group by isbn
    """

    @classmethod
    def get_wish_counts(cls, isbn_list: list):
        from app.models.wish import Wish
        # 返回结果为一个列表中嵌套元祖
        count_list = db.session.query(func.count(Wish.id), Wish.isbn).filter(
            # 需要传递条件表达式,而不是赋值表达式
            Wish.launched == False,
            Wish.isbn.in_(isbn_list),
            Wish.status == 1).group_by(Wish.isbn).all()

        # 将元祖改为包含字典的列表
        return [{"count": record[0], "isbn": record[1]} for record in count_list]

    @property
    def book(self):
        bee_book = BeeBook()
        bee_book.search_by_isbn(self.isbn)

        return bee_book.first

    # 从db中查询出所有的未赠送的书籍
    @classmethod
    def recent(cls):
        recent_gifts = Gift.query.filter_by(launched=False
                                            ).group_by(Gift.isbn).order_by(
            desc(Gift.create_time)).limit(current_app.config['RECENT_UPLOAD_PAGE_BOOKS_NUMBER']).distinct().all()

        return recent_gifts
