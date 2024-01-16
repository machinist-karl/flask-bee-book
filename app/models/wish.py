from sqlalchemy import Column, Integer, Boolean, ForeignKey, String, desc, func
from sqlalchemy.orm import relationship

from app.models.base import Base, db
from app.spider.bee_book import BeeBook


class Wish(Base):
    id = Column(Integer, primary_key=True)
    # 使用relationship()标识User模型与Gift模型之间的关系
    user = relationship('User')
    # user.id中的user取是user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'))
    # 使用isbn号与Book模型关联
    isbn = Column(String(15), nullable=False)
    launched = Column(Boolean, default=False)  # 标记该本书籍是否已赠送

    @classmethod
    def get_user_wishes(cls, uid):
        wishes = Wish.query.filter_by(uid=uid, launched=False).order_by(desc(Wish.create_time)).all()

        return wishes

    @classmethod
    def get_wish_counts(cls, isbn_list: list):
        from app.models.gift import Gift
        # 返回结果为一个列表中嵌套元祖
        count_list = db.session.query(func.count(Gift.id), Gift.isbn).filter(
            # 需要传递条件表达式,而不是赋值表达式
            Gift.launched == False,
            Gift.isbn.in_(isbn_list),
            Gift.status == 1).group_by(Gift.isbn).all()

        # 将元祖改为包含字典的列表
        return [{"count": record[0], "isbn": record[1]} for record in count_list]

    @property
    def book(self):
        bee_book = BeeBook()
        bee_book.search_by_isbn(self.isbn)

        return bee_book.first
