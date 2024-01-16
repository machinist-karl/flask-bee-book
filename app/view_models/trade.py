# 用于映射book detail页面上底部信息
# 即某本书的赠送者列表,或某本书心愿者列表
from app.view_models.book import BookViewModel


class TradeInfo:
    def __init__(self, goods):
        self.total = 0  # 拥有者/心愿者人数
        self.trades = []  # 拥有者/心愿者名单
        self.__parse(goods)

    def __parse(self, goods):
        self.total = len(goods)
        self.trades = [self._map_to_trade(single) for single in goods]

    def _map_to_trade(self, single):
        if single.create_datetime:
            time = single.create_datetime.strftime('%Y-%m-%d')
        else:
            time = 'Unknown time'
        return dict(
            user_name=single.user.nickname,
            time=time,
            id=single.id
        )


class MyTrade:
    def __init__(self, mine_trades, trade_count_list):
        self.trades = []
        self.__mine_trades = mine_trades
        self.__trade_count_list = trade_count_list
        self.trades = self.__parse()

    def __parse(self):
        temp_gifts = []
        for trade in self.__mine_trades:
            my_trade = self.__matching(trade)
            temp_gifts.append(my_trade)

        return temp_gifts

    def __matching(self, trade):
        count = 0
        for item in self.__trade_count_list:
            if trade.isbn == item['isbn']:
                count = item['count']

        result = {
            'id': trade.id,
            'trade_count': count,
            'book': BookViewModel(trade.book)
        }

        return result
