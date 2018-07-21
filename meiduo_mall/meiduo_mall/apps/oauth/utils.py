from urllib.parse import urlencode

from django.conf import settings


class QAuthQQ(object):
    """
    QQ认证辅助工具类
    """

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE

    def get_qq_url(self):
        # 　QQ登陆url组建
        data_dict = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state
        }
        # 构建url  请求地址： PC网站：https://graph.qq.com/oauth2.0/authorize
        qq_url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(data_dict)  # 将data_dict字典转换为url路径中的查询字符串

        return qq_url
