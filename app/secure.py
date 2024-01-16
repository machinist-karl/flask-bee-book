DEBUG = False
PORT = 8081
# 表示支持外网访问
HOST = '0.0.0.0'
THREADED = True  # 是否开启多线程模式
# 第三方图书查询调用API key
API_KEY = '例如douban图书查询的API'

""" 
    数据库连接配置
        连接配置变量名称需要固定为 : SQLALCHEMY_DATABASE_URI
        如果密码中包含有特殊字符则需要转义,例如'&'使用'%26'来替代
        支持pymysql、cymysql
"""
SQLALCHEMY_DATABASE_URI = '数据库连接'
SECRET_KEY = '61db1bbd91ddeb84d1d188bcddc3fa54'
TOKEN_ALGORITHM = 'HS256'

# Email 配置
MAIL_SERVER = '邮件服务器地址，简易采用第三方的,如qq'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TSL = False
# 填写邮箱地址
MAIL_USERNAME = 'sample@qq.com'
# 密码，不是登录邮箱的密码,类似于token,可参考qq邮箱的获取
MAIL_PASSWORD = 'wftaptpkgvxkbghc'
MAIL_SUBJECT_PREFIX = '[设置邮件的标题前缀]'
# MAIL_SENDER = '可以不填写'

