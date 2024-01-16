from flask import flash, url_for, render_template, request, redirect
from flask_login import login_required, current_user
from sqlalchemy import desc
from sqlalchemy.sql.elements import or_

from . import web
from ..forms.forms_book import DriftForm
from ..libs.email import send_email
from ..libs.enums import ApplyStatus
from ..models.base import db
from ..models.drift import Drift
from ..models.gift import Gift
from ..models.user import User
from ..models.wish import Wish
from ..view_models.book import BookViewModel
from app.view_models.drift import DriftCollection


# gid: 礼物的ID
@web.route('/drift/<int:gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    current_gift: Gift = Gift.query.get_or_404(gid)
    # 校验申请人和发布人不能是同一个人
    if current_gift.is_yourself_gift(current_user.id):
        flash('这本书是你自己的呀^_^,不能向自己索要书籍喔!')
        # 将页面重定向到书籍详情页面
        return redirect(url_for('web.book_detail', isbn=current_gift.isbn))

    # 业务规则校验,申请人的积分不能小于1且申请人每得到2本书,必须成功赠送1本书
    can = current_user.can_send_drift()
    if not can:
        return render_template("not_enough_beans.html", beans=current_user.beans)

    # 图书赠送请求订单页面上信息填完后，点击提交按钮
    # 跳转到
    form = DriftForm(request.form)
    if request.method == "POST" and form.validate():
        save_drift(form, current_gift)
        # 发送邮件给礼物的提供者，告知其有人想要礼物书
        send_email(current_gift.user.email,
                   "收到一份赠书请求", 'email/get_gift.html',
                   wisher=current_user, gift=current_gift)

        return redirect(url_for("web.pending"))

    # 用于赠送者的简要信息展示在drift.html页面上
    gifter = current_gift.user.summary

    # Get请求跳转到图书赠送请求订单页面
    return render_template("drift.html",
                           gifter=gifter, user_beans=current_user.beans, form=form)


@web.route('/pending')
@login_required
def pending():
    # 需要查询我的所有赠送记录和被赠送记录
    # or_表示或者关系
    drifts = Drift.query.filter(or_(Drift.requester_id == current_user.id,
                                    Drift.gifter_id == current_user.id)
                                ).order_by(desc(Drift.create_time)).all()
    views = DriftCollection(drifts, current_user.id)

    return render_template("pending.html", drifts=views.data)


# 撤销自定创建的申请书单
# 修改申请单状态
@web.route('/drift/<int:did>/redraw')
@login_required
def redraw_drift(did):
    with db.auto_commit():
        # Drift.requester_id == current_user.id防止越权操作,即防止A操作B的申请单
        drift: Drift = Drift.query.filter(Drift.requester_id == current_user.id,
                                          Drift.id == did).first_or_404()
        """
            pending=ApplyStatus.REDRAW, 将调用drift模型中的方法
            进行转换将枚举转换成DB中的数字型
            @pending.setter
            def pending(self, status):
                self._pending = status.value
        """
        # 将申请单状态改为撤销
        drift.pending = ApplyStatus.REDRAW
        # 将积分恢复
        current_user.beans += 1

    return redirect(url_for('web.pending'))


# 书籍所有者拒绝申请人
@web.route('/drift/<int:did>/reject')
@login_required
def reject_drift(did):
    with db.auto_commit():
        drift: Drift = Drift.query.filter(Drift.requester_id == current_user.id,
                                          Drift.id == did).first_or_404()
        # 将申请单状态改为拒绝
        drift.pending = ApplyStatus.REJECT
        # 查询出申请人的信息
        requester: User = User.query.get_or_404(drift.requester_id)
        # 将申请人的积分退换
        requester.beans += 1

    return redirect(url_for('web.pending'))


# 已邮寄
@web.route('/drift/<int:did>/mailed')
@login_required
def mailed_drift(did):
    with db.auto_commit():
        # select * from dirft where gifter_id=赠送者id and id=页面所传订单号
        drift: Drift = Drift.query.filter_by(gifter_id=current_user.id, id=did).first_or_404()
        # 修改订单状态为已邮寄
        drift.pending = ApplyStatus.MAILED
        # 将赠送者积分增减
        current_user.id += 1
        # 修改gift表中礼物的状态为已赠送
        gift: Gift = Gift.query.filter_by(id=drift.gift_id).first_or_404()
        gift.launched = True
        # 修改申请者心愿单表中礼物的状态
        # update wish set launched=1 where isbn=drift.isbn and uid=drift.requester_id and launched=False
        # launched表示书籍是否已赠送
        # 该种写法的功能和上面更新礼物表中的标志位一致
        Wish.query.filter_by(isbn=drift.isbn, uid=drift.requester_id, launched=False).update({Wish.launched: True})

        return redirect(url_for("web.pending"))


def save_drift(drift_form: DriftForm, current_gift):
    with db.auto_commit():
        # 创建drift模型
        drift = Drift()
        # drift_form继承Form
        # 调用Form的populate_obj方法,将request中的表单传递到模型对象中
        drift_form.populate_obj(drift)

        drift.gift_id = current_gift.id
        drift.requester_id = current_user.id
        drift.requester_nickname = current_user.nickname
        drift.gifter_nickname = current_gift.user.nickname
        drift.gifter_id = current_gift.user.id

        book = BookViewModel(current_gift.book)
        drift.book_title = book.title
        drift.book_author = book.author
        drift.book_img = book.image
        drift.isbn = book.isbn

        # 更新用户积分
        current_user.beans -= 1
        # 插入数据,需要显式调用add方法
        db.session.add(drift)
