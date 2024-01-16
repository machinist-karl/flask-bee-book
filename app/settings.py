"""
    业务参数配置
"""
from datetime import timedelta

# 查询分页时Page Size大小
PER_PAGE = 10

# cookie保持时长,默认为365天
REMEMBER_COOKIE_DURATION = timedelta(days=7)

# 每上传一本书赠送积分数
PER_BOOK_UPLOAD_GIVEN_BEANS = 0.5

# 最近上传页面配置页面最大书籍显示的数量
RECENT_UPLOAD_PAGE_BOOKS_NUMBER = 30

# debug模式下打印详细SQL语句
SQLALCHEMY_ECHO = True
