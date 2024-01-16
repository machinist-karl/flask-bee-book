from flask import Flask
from app.models.book import db
from flask_login import LoginManager
from flask_mail import Mail

login_manager = LoginManager()
mail = Mail()


def create_app():
    app = Flask(__name__)
    # 系统,环境参数配置
    app.config.from_object("app.secure")
    # 业务参数配置
    app.config.from_object("app.settings")
    # 注册蓝图到flask核心上
    register_blueprint_by_self(app)

    # 初始化login manager插件
    login_manager.init_app(app)

    # 这里将web.login的路由装饰器赋值给登录的entrypoint
    # 如果用户未获得授权访问某些页面，则会跳转到登录页面
    login_manager.login_view = 'web.login'
    login_manager.login_message = '请先登录或注册'

    mail.init_app(app)

    # 注册数据库连接到flask核心上
    with app.app_context():
        db.init_app(app)
        # 将model中的类全部映射到数据库中,即建表
        db.create_all()

    return app


# web只会被导入一次
def register_blueprint_by_self(app):
    from app.web.book import web
    """
        注意这里调用的是Flask父类App中的register_blueprint()方法
        其参数为一个蓝图对象
    """
    app.register_blueprint(web)
