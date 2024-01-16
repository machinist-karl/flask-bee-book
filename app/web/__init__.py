"""
    蓝图 : 解决如果视图不定义在核心中，而无法找到路由的问题
        1、核心(Flask核心对象) --> 蓝图-1，蓝图-2, 蓝图-3 --> 视图函数
        2、一个核心可以拔插多个蓝图,一个蓝图可拔插多个视图
        3、蓝图需要注册在Flask的核心对象上，否则无法使用

        name: 自定义蓝图名称
        import_name : 指定蓝图所在的包（带有__init__的文件夹）/模块（一个朋友文件）
"""
from flask import Blueprint, render_template

web = Blueprint('web', __name__)


# 面向切面的编程思想
# 只要遇到404错误都会返回自定的404页面
# 该函数中可以编写任意业务逻辑，如记录日志
@web.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


from app.web import book
from app.web import auth
from app.web import gift
from app.web import wish
from app.web import main
from app.web import drift
