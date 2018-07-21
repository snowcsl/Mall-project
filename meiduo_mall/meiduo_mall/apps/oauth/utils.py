from urllib.parse import urlencode, parse_qs
import requests
from django.conf import settings
import json

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

    def get_access_token(self,code):
        # 构建参数数据
        data_dict = {
            'grant_type':'authorization_code',
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'redirect_uri':self.redirect_uri,
            'code':code
        }

        # 构建url
        # PC网站：https://graph.qq.com/oauth2.0/token
        access_url = 'https://graph.qq.com/oauth2.0/token?'+urlencode(data_dict)

        try:
            # 发送请求
            response = requests.get(access_url)

            # 提取数据
            # access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE14
            data = response.text # 返回查询字符串的形式

            # 转化为字典
            data = parse_qs(data)  # 将data查询字符串格式数据转换为python的字典
        except:
            raise Exception('qq请求失败')

        # 提取access_token
        access_token = data.get('access_token',None)

        if not access_token:
            raise Exception('access_token获取失败')

        return access_token[0]

    def get_open_id(self,access_token):
        # 构建url
        # PC网站：https://graph.qq.com/oauth2.0/me  需携带的参数:access_token
        url= 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        try:

            # 发送请求
            response = requests.get(url)

            # 提取数据
            # callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );
            # code=asdasd&msg=asjdhui  错误的时候返回的结果
            data = response.text

            data = data[10:-3]   # 通过切片切除字典形式的字符串
        except:
            raise Exception('qq请求失败')
        try:

            # 转化为字典
            data_dict = json.loads(data)
            # 获取openid
            openid = data_dict.get('openid')
        except:
            raise Exception('openid获取失败')
        return openid















