from flask import render_template, flash, url_for, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from . import web
from app.models.base import db
from ..libs.email import send_email
from ..models.gift import Gift
from ..models.wish import Wish
from ..view_models.trade import MyTrade


@web.route('/my/wish')
@login_required
def my_wish():
    uid = current_user.id
    mine_wishes = Wish.get_user_wishes(uid)
    isbn_list = [wish.isbn for wish in mine_wishes]
    wishes_count_list = Wish.get_wish_counts(isbn_list)
    view_model = MyTrade(mine_wishes, wishes_count_list)

    return render_template('my_wish.html', wishes=view_model.trades)


# 将意向之书加入到心愿单
@web.route('/wish/book/<isbn>')
@login_required
def save_to_wish(isbn):
    if current_user.can_save_to_list(isbn):
        # 上下文对象无实际返回对象时, 无需增加as
        with db.auto_commit():
            wish = Wish()
            wish.isbn = isbn
            # 从cookie中获取登录用户的user id
            # 从flask_login插件中导入current_user
            # models/user下的load_user()函数生成该current_user
            wish.uid = current_user.id
            db.session.add(wish)
    else:
        flash("本书已存在于您的心愿或者赠送清单,请勿重复添加")

    return redirect(url_for("web.book_detail", isbn=isbn))


# wid: 用户心愿id
@web.route('/satisfy/wish/<int:wid>')
@login_required
def satisfy_wish(wid):
    wish: Wish = Wish.query.get_or_404(wid)
    gift: Gift = Gift.query.filter_by(uid=current_user.id, isbn=wish.isbn).first()
    if gift:
        flash("您还未上传此书,请点击加入到赠送清单！")
    else:
        send_email(Wish.user.email, '有人愿意送你一好书！',
                   'email/satisify_wish.html', wish=wish, gift=gift)
        flash("有人愿意送你一本书，若对方同意您的赠送,您将会收到一张订单！")

    return redirect(url_for('web.book_detail', isbn=wish.isbn))


# 取消心愿
@web.route('/wish/book/<isbn>/redraw')
@login_required
def redraw_from_wish(isbn):
    wish: Wish = Wish.query.filter_by(isbn=isbn, uid=current_user.id, launched=False).first_or_404()
    with db.auto_commit():
        wish.delete()

    return redirect(url_for("web.my_wish"))
