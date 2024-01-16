from wtforms import Form, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo

from app.models.user import User


class ResetPasswordForm(Form):
    password1 = PasswordField('新密码', validators=[
        DataRequired(), Length(6, 20, message='密码长度至少需要在6到20个字符之间'),
        EqualTo('password2', message='两次输入的密码不相同')])
    password2 = PasswordField('确认新密码', validators=[
        DataRequired(), Length(6, 20)])


class ChangePasswordForm(Form):
    old_password = PasswordField('原有密码', validators=[DataRequired()])
    new_password1 = PasswordField('新密码', validators=[
        DataRequired(), Length(6, 10, message='密码长度至少需要在6到20个字符之间'),
        EqualTo('new_password2', message='两次输入的密码不一致')])
    new_password2 = PasswordField('确认新密码字段', validators=[DataRequired()])


class EmailForm(Form):
    # 需要手工安装email-validator : pip install email-validator
    email = StringField('电子邮件', validators=[DataRequired(message='邮箱不能为空'), Length(8, 64),
                                                Email(message='电子邮箱不符合规范')])


class LoginForm(EmailForm):
    # 需要手工安装email-validator : pip install email-validator
    # email = StringField('电子邮件', validators=[DataRequired(message='邮箱不能为空'), Length(1, 64),
    # Email(message='电子邮箱不符合规范')])

    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'), Length(6, 20)])


class RegisterForm(LoginForm):
    nickname = StringField('昵称', validators=[
        DataRequired(message='用户名不能为空'), Length(2, 10, message='昵称至少需要两个字符，最多10个字符')])

    # 用户自定义校验器,由框架调用
    def validate_email(self, field):
        """
            1. User.query等价于db.session.query(Model),Model即为Bean对象
            2. field具体值由框架从wtforms中获取
            3. 用户自定义业务验证器,必须以validate_开头，后接需要验证的参数名称
            4. validate_email无需显式调用, 框架会根据结尾_email自动匹配调用
            5. first()将触发该查询，无论查询结果的数量，只取第一条
            6. filter_by()的参数可以传入一组查询条件
        """
        # 从db查询该邮箱是否存在,如果存在则将该错误
        if User.query.filter_by(email=field.data).first():
            # 校验如果不通过，则该条信息将会被传递到forms.errors中,显示在前端
            raise ValidationError("该邮箱已注册，请更换邮箱再试")

    # 校验用户名是否被注册
    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError("该用户名已被他人注册，请更换再试")
