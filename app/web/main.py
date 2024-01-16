from flask import render_template
from flask_login import current_user, login_required

from app.view_models.book import BookViewModel
from . import web
from ..models.gift import Gift


# 显示未被赠送图书的列表
@web.route('/')
def index():
    # 获取Gift模型表中的所有数据
    recent_gifts = Gift.recent()
    # 根据gift中的isbn号调用BeeBook中的接口获取图书详情
    # 使用BookViewModel将BeeBook获取的接口返回数据格式化为页面所需要的数据
    books = [BookViewModel(gift.book) for gift in recent_gifts]

    return render_template('index.html', recent=books)


@web.route('/personal')
@login_required
def personal_center():
    return render_template('personal.html', user=current_user.summary)


