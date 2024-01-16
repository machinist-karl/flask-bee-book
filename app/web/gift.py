from flask import current_app, flash, redirect, url_for, render_template
from flask_login import login_required, current_user

from . import web
from ..libs.enums import ApplyStatus
from ..models.drift import Drift
from ..models.gift import Gift
from app.models.base import db
from ..view_models.trade import MyTrade


@web.route('/my/gifts')
@login_required
def my_gifts():
    uid = current_user.id
    # 获取赠送人的所有待赠送书籍列表
    mine_gifts = Gift.get_user_gifts(uid)
    # 获取赠书人的所有书的isbn号
    isbn_list = [gift.isbn for gift in mine_gifts]
    wish_count_list = Gift.get_wish_counts(isbn_list)
    view_model = MyTrade(mine_gifts, wish_count_list)

    return render_template('my_gifts.html', gifts=view_model.trades)


# 赠送此书功能
@web.route('/gifts/book/<isbn>')
@login_required
def save_to_gifts(isbn):
    if current_user.can_save_to_list(isbn):
        # 上下文对象无实际返回对象时, 无需增加as
        with db.auto_commit():
            gift = Gift()
            gift.isbn = isbn
            # 从cookie中获取登录用户的user id
            # 从flask_login插件中导入current_user
            # models/user下的load_user()函数生成该current_user
            gift.uid = current_user.id
            # 增加用户的积分
            current_user.beans += current_app.config['PER_BOOK_UPLOAD_GIVEN_BEANS']
            db.session.add(gift)
    else:
        flash("本书已存在于您的心愿或者赠送清单,请勿重复添加")

    return redirect(url_for("web.book_detail", isbn=isbn))


#  撤销赠送清单中的书籍
@web.route('/gifts/<gid>/redraw')
def redraw_from_gifts(gid):
    gift: Gift = Gift.query.filter_by(id=gid, uid=current_user.id, launched=False).first_or_404()

    # 业务规则，订单表中存在的礼物为交易状态,不允许提供者撤销,必须先处理交易
    drift: Drift = Drift.query.filter_by(gift_id=gift.id, requester_id=current_user.id, pending=ApplyStatus.WAITING).first()
    if drift:
        flash("该礼物正处于交易状态,请先前往订单表中处理")
    else:
        with db.auto_commit():
            current_user.beans -= current_app.config['PER_BOOK_UPLOAD_GIVEN_BEANS']
            # 将条记录的标志位置为已删除
            gift.delete()

    return redirect(url_for("web.my_gifts"))
