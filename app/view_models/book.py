from app.spider.bee_book import BeeBook


# ISBN搜索,从原始数据中取出页面模板中需要的数据
class BookViewModel:
    def __init__(self, book: BeeBook):
        self.title = book['title']
        self.publisher = book['publisher']
        self.author = book['author']
        self.image = book['image']
        self.price = book['price']
        self.summary = book['summary']
        self.isbn = self.get_isbn(book)
        self.pages = book['pages']
        self.pubdate = book['pubdate']
        self.binding = book['binding']

    @staticmethod
    def get_isbn(book: BeeBook) -> str:
        if book['isbn13']:
            return book['isbn13']
        if book['isbn10']:
            return book['isbn10']
        else:
            return "Unknown ISBN"

    """
        1. 使用内置过滤器filter判断BookViewModel中的实例属性是否为空
        filter(function, iterable)
        2. 使用lambda判断属性是否为空,为空则不添加属性进行分割
        "/".join('book') --> b/o/o/k
        3. 对应templates --> search_result.html中的{{book.brief}},将该方法作为属性使用
    """

    @property
    def brief(self):
        short = filter(lambda p: True if p else False,
                       [self.author, self.publisher, self.price])

        # self.author类型为一个list，需要将其手工转换成字符串
        return " / ".join('%s' % x for x in short)


# 关键字搜索,从原始数据中取出页面模板中需要的数据
class BookCollection:
    def __init__(self):
        self.total = 0
        self.books = []
        self.keyword = ''

    def fill(self, bee_book: BeeBook, keyword):
        self.total = bee_book.total
        self.keyword = keyword
        # 关键字搜索返回为一组图书列表,单个图书信息即为BookViewModel
        # 使用列表推导式将单个book添加到books中
        self.books = [BookViewModel(book) for book in bee_book.books]
