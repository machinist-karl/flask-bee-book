from enum import Enum


class ApplyStatus(Enum):
    # 申请订单的4种状态
    WAITING = 1
    SUCCESS = 2
    REJECT = 3
    REDRAW = 4

    @classmethod
    def pending_str(cls, status, key):
        key_map = {
            cls.WAITING: {
                'requester': '等待对方邮寄',
                'gifter': '等待你邮寄'
            },
            cls.REJECT: {
                'requester': '对方已拒绝',
                'gifter': '你已拒绝'
            },
            cls.REDRAW: {
                'requester': '你已撤销',
                'gifter': '对方已撤销'
            },
            cls.SUCCESS: {
                'requester': '对方已邮寄',
                'gifter': '你已邮寄，交易完成'
            }
        }
        return key_map[status][key]
