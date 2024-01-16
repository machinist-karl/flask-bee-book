import json

from flask import render_template, flash
from flask import request
from flask_login import current_user

from app.models.gift import Gift
from app.models.wish import Wish
from app.spider.bee_book import BeeBook
from app.libs.helper import is_isbn_or_key
from app.view_models.book import BookCollection, BookViewModel
from app.view_models.trade import TradeInfo
from app.web import web
from app.forms.forms_book import SearchForm


# @web.route('/register', methods=['GET', 'POST'])
# def register():
#     print("进入register页面")
#     return "进入register页面"


"""
    需求 :
        将请求从'/book/search/<q>/<page>'
        改为/book/search&q=xxx&page=1
    步骤 : 
        1、需要引入Flask的request库
        2、去除search()中的入参
    注意:
        request作为一个代理，必须要有Http请求的上下文，其本质为一个代理
        在本例中必须配合Blueprint使用，不能直接实例化获取请求参数        
"""


# @web.route('/book/search/<q>/<page>')
@web.route('/book/search')
def search():
    """
         校验过程 :
             1、创建SearchForm的对象时传递一个request.args字典对象（表单）
             2、显示调用SearchForm父类中的的实例方法validate(),开启数据校验
             3、取出表单中的q和page与SearchForm对象中的q和page属性进行映射
             4、调用这两个属性中定义的校验规则进行校验
     """
    form = SearchForm(request.args)
    books = BookCollection()
    # 表单或请求数据映射后进行校验
    if form.validate():
        # 当校验通过后，取属性名和属性值,执行后续逻辑
        q = form.q.data.strip()
        page = form.page.data
        isbn_or_key = is_isbn_or_key(q)
        bee_book = BeeBook()

        if isbn_or_key == 'isbn':
            bee_book.search_by_isbn(q)
        else:
            bee_book.search_by_keyword(q, page)
        books.fill(bee_book, q)
    else:
        flash("您输入的查询关键字不符合要求,请重新输入")

    """
        Flask 默认的静态文件夹名称为static,注册在核心对象上,也可以注册在蓝图上
        同样页面的模板文件夹为templates，可以注册在核心对象上,也可以注册在蓝图上
        app = Flask(__name__, static_folder=''或者template_folder='')
    """
    # templates中的html页面
    return render_template("search_result.html", books=books, form=form)


@web.route('/book/<isbn>/detail')
def book_detail(isbn):
    has_in_gifts = False
    has_in_wishes = False

    bee_book = BeeBook()
    bee_book.search_by_isbn(isbn)
    # 页面数据模型对接口数据进行二次封装
    book = BookViewModel(bee_book.first)

    # 判断当前用户否否已登录
    if current_user.is_authenticated:
        # 判断用户是否为赠送者
        if Gift.query.filter_by(isbn=isbn, uid=current_user.id, launched=False).first():
            has_in_gifts = True
        # 判断用户是否为该书的心仪用户
        if Wish.query.filter_by(isbn=isbn, uid=current_user.id, launched=False).first():
            has_in_wishes = True
    # 将礼物表中该本书中所有的赠送者都查询出
    all_gifts = Gift.query.filter_by(isbn=isbn, launched=False).all()
    # 将心愿表中该本书中所有需要本书的人都查询出
    all_wishes = Wish.query.filter_by(isbn=isbn, launched=False).all()

    # 使用TradeInfo模型麻将该本书从心愿单和礼物单中的记录加载出来显示在页面
    gifts_list = TradeInfo(all_gifts)
    wishes_list = TradeInfo(all_wishes)

    # 将数据塞入页面模板中
    return render_template("book_detail.html",
                           book=book, wishes=wishes_list,
                           gifts=gifts_list, has_in_gifts=has_in_gifts,
                           has_in_wish=has_in_wishes)

