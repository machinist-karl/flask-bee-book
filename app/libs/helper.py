

# 判断用户输入是ISBN或者普通关键字
def is_isbn_or_key(word: str):
    isbn_or_key = 'key'
    # 13位的ISBN号
    if len(word) == 13 and word.isdigit():
        isbn_or_key = 'isbn'
    # 如果是ISBN,去除可能存在的"-"
    short_isbn = word.replace("-", "")
    # 10位的ISBN号
    if "-" in word and len(short_isbn) == 10 and short_isbn.isdigit():
        isbn_or_key = 'isbn'

    return isbn_or_key
