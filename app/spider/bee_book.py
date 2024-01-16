from app.libs.httptools import HttpTools
# 获取当前的Flask核心对象(代理模式),核心对象不要导入,即不雅哟导入main.py
# 用于在其包中引用flask核心对象
from flask import current_app


# 待处理 : 将isbn_url、keyword_url放入到secure文件中
class BeeBook:
    isbn_url = 'https://api.xxxx.com/modify_path/book/isbn/{}?apikey={}'
    keyword_url = 'https://api.xxxx.com/modify_path/book/search?q={}&apikey={}&start={}&count={}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    def __init__(self):
        self.total = 0
        self.books = []

    def search_by_isbn(self, isbn: str):
        url = self.isbn_url.format(isbn, current_app.config['API_KEY'])
        result = HttpTools.post(url, self.headers)
        self.__fill_single(result)

    def search_by_keyword(self, keyword: str, page=1):
        url = self.keyword_url.format(keyword, current_app.config['API_KEY'], self.calculate_start(page),
                                      current_app.config['PER_PAGE'])
        result = HttpTools.post(url, self.headers)
        self.__fill_collection(result)

    def __fill_single(self, data):
        if data:
            self.total = 1
            self.books.append(data)

    def __fill_collection(self, data):
        self.total = data['total']
        self.books = data['books']

    def calculate_start(self, page):  # 计算Page index
        return (page - 1) * current_app.config['PER_PAGE']

    # 用户点击某本书籍时，进入该书籍的详情页
    # isbn搜索或者是关键字查询出来的书籍都会被放入到名称为books的list中
    # 对于通过搜索需要进入书籍详情页的，只需要/只能获取books中的第一条数据
    @property
    def first(self):
        return self.books[0] if self.total >= 1 else None
