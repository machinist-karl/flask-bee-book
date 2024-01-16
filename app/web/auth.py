from flask_login import login_user, logout_user, login_required, current_user

from app.web import web
from flask import render_template, request, redirect, url_for, flash

from app.forms.forms_auth import RegisterForm, LoginForm, EmailForm, ResetPasswordForm, ChangePasswordForm
from app.models.user import User
from app.models.base import db
from app.libs.email import send_email

"""
    web下的各个controller需要在模块中进行导入
    否则将无法路由到相关的页面
    即需要在__init__.py文件下输入导入语句
    from app.web import book
    from app.web import auth
"""


# 用户注册, 支持2种请求方式
@web.route('/register', methods=['GET', 'POST'])
def register():
    """
        从request中取数据需要注意方式，否则无法取到请求数据
        如: form表单中取值,args取值,json取值,value取值等
    """
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        with db.auto_commit():
            # 将用户信息存储到db
            # 使用db.auto_commit()管理db的事务
            user = User()
            user.set_attrs(form.data)
            db.session.add(user)
            # 当注册成功后,重定向到登录页面让用户登录
            # 需要使用url_for()生成重定向地址
            # 注册成功直接跳转到登录页面
            return redirect(url_for('web.login'))

    # 注册失败任然停留在注册页面
    return render_template('auth/register.html', form=form)


@web.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # 从db中获取用户
        user: User = User.query.filter_by(email=form.email.data).first()
        # 判断用户是否存在并且密码是否相同
        if user and user.check_password(form.password.data):
            # 登录成功后，生成cookie并返回给客户端
            # 调用UserMixin中的get_id()方法，将用户id作为cookie
            login_user(user, remember=True)

            """
                登录成功后,flask_login会在request后附加next参数
                如: http://domian:8080/login?next=%2Fmy%2Fgifts
                将页面重定向到用户开始访问的页面（需要登录才能访问的页面）
            """
            next_addr_param: str = request.args.get('next')
            # 登录成功后, 如果next参数没有值,即跳转页面不存在,则重定向到首页
            # next后一般参数值为/a/b，即以/开头,如果不是，页重定向到首页
            # 这样为了防止页面重定向攻击
            if not next_addr_param or not next_addr_param.startswith("/"):
                next_addr_param = url_for("web.index")
                return redirect(next_addr_param)
        else:
            flash("账号不存在或密码错误")

    return render_template('auth/login.html', form=form)


@web.route('/reset/password', methods=['GET', 'POST'])
def forget_password_request():
    form = EmailForm(request.form)
    if request.method == 'POST':
        if form.validate():
            account_email = form.email.data
            # 如果db中找不到该邮箱号,则first_or_404()会抛出异常且后续步骤不会被执行
            # 避免后续增加if user为空的语句和处理逻辑
            user: User = User.query.filter_by(email=account_email).first_or_404()
            send_email(account_email, '重置您的密码',
                       'email/reset_password.html',
                       user=user, token=user.generate_token())
            flash("一封邮件已发送到您的" + account_email + "邮箱中,请及时查收!")

    return render_template('auth/forget_password_request.html', form=form)


# 发送密码到邮箱后的链接验证
@web.route('/reset/password/<token>', methods=['GET', 'POST'])
def forget_password(token):
    form = ResetPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        is_success = User.reset_password(token, form.password1.data)
        if is_success:
            flash("重置密码成功，请使用新密码重新登录")
            return redirect(url_for("web.login"))
        else:
            flash("重置密码失败，也许超时，请重新再试")
    return render_template('auth/forget_password.html', form=form)


@web.route('/change/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        if not current_user.check_password(form.old_password.data):
            flash("原有密码错误,请重新输入")
            return redirect(url_for("web.change_password"))

        if form.new_password1.data != form.new_password2.data:
            flash("两次输入的新密码不一致，请重新输入")
            return redirect(url_for("web.change_password"))

        with db.auto_commit():
            # current_user.password属性为方法,自动调用setter方法
            current_user.password = form.new_password1.data
            flash("更新密码成功")
        return redirect(url_for("web.personal_center"))

    return render_template('auth/change_password.html', form=form)


@web.route('/logout')
def logout():
    logout_user()
    # Blueprint --> 注册web蓝图 --> main.py下的index函数
    return redirect(url_for('web.index'))
