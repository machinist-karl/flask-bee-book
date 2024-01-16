import requests


class HttpTools:

    # 若不访问类的属性,则无需使用@classmethod
    @staticmethod
    def post(url: str, headers: dict, return_json: bool = True):

        resp = requests.post(url=url, headers=headers)
        # python三元表达式
        if resp.status_code != 200:
            return {} if return_json else ""
        return resp.json() if return_json else resp.text  # resp.json()为一个dict

    @staticmethod
    def get(url: str, headers: dict, return_json: bool = True):

        resp = requests.get(url=url, headers=headers)
        # python三元表达式
        if resp.status_code != 200:
            return {} if return_json else ""
        return resp.json() if return_json else resp.text
