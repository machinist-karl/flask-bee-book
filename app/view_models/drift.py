from app.libs.enums import ApplyStatus
from app.models.drift import Drift


class DriftViewModel:
    def __init__(self, drift: Drift, current_user_id):
        self.data = {}
        self.data = self._parse(drift, current_user_id)

    @staticmethod
    def requester_or_gifter(drift: Drift, current_user_id):
        if drift.requester_id == current_user_id:
            you_are = 'requester'
        else:
            you_are = 'gifter'

        return you_are

    def _parse(self, drift: Drift, current_user_id):
        you_are = self.requester_or_gifter(drift, current_user_id)
        pending_status = ApplyStatus.pending_str(drift.pending, you_are)
        r = {
            'you_are': you_are,
            'drift_id': drift.id,
            'book_title': drift.book_title,
            'book_author': drift.book_author,
            'book_img': drift.book_img,
            'date': drift.create_datetime.strftime('%Y-%m-%d'),
            'operator': drift.requester_nickname if you_are != 'requester' \
                else drift.gifter_nickname,
            'message': drift.message,
            'address': drift.address,
            'status_str': pending_status,  # 订单状态
            'recipient_name': drift.recipient_name,
            'mobile': drift.mobile,
            'status': drift.pending
        }
        return r


class DriftCollection:
    def __init__(self, drifts, current_user_id):
        self.data = []
        self._parse(drifts, current_user_id)

    def _parse(self, drifts, current_user_id):
        for drift in drifts:
            tmp = DriftViewModel(drift, current_user_id)
            self.data.append(tmp.data)
