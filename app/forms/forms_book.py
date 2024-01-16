from wtforms import Form, StringField, IntegerField
from wtforms.validators import Length, NumberRange, DataRequired, Regexp


# 用于Search视图中request参数的验证
class SearchForm(Form):
    # 设置查询查询内容参数q的校验规则
    # DataRequired : if the data is a string type, a string containing only whitespace characters is considered false
    # 防止q=空格&page=1这种形式的请求
    q = StringField(
        validators=[DataRequired(), Length(min=1, max=30, message=" 查询内容为空或者查询关键字长度不符合要求")])
    # 设置查询page index参数的校验规则，default=1表示该值为空的情况下使用默认值1
    # 注意这里设置的是int值的范围,不是值的长度
    # 对于数字类型,不能调用len(), 因为没有实现__len()__魔法函数
    page = IntegerField(validators=[NumberRange(min=1, max=999, message="页码必须在[1 - 999]之间")], default=1)


class DriftForm(Form):
    recipient_name = StringField(
        '收件人姓名', validators=[DataRequired(), Length(min=2, max=20,
                                                         message='收件人姓名长度必须在2到20个字符之间')])
    mobile = StringField('手机号', validators=[DataRequired(),
                                               Regexp('^1[0-9]{10}$', 0, '请输入正确的手机号')])
    message = StringField('留言')
    address = StringField(
        '邮寄地址', validators=[DataRequired(),
                                Length(min=10, max=70, message='地址还不到10个字吗？尽量写详细一些吧')])
