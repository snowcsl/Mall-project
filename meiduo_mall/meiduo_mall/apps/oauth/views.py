from urllib.parse import urlencode

from urllib.request import urlopen
from rest_framework.settings import api_settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from oauth.models import OAuthQQUser
from .exceptions import OAuthQQAPIError
from oauth.utils import OAuthQQ
from django.conf import settings
import logging

logger = logging.getLogger('django')


# Create your views here.


#  url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
class QQAuthURLView(APIView):
    """
    获取Q登陆的url地址  ?next=xxx

    """

    def get(self, request):
        # 获取next参数
        next = request.query_params.get('next')

        # 拼接QQ登录的地址
        oauth_qq = OAuthQQ(state=next)
        login_url = oauth_qq.get_qq_login_url()

        # 返回
        return Response({'login_url': login_url})

        # def get(self, request):
        #     # 获取state
        #     state = request.query_params.get('state', settings.QQ_STATE)
        #
        #     # qq登录url参数构建
        #     data_dict = {
        #         'response_type': 'code',
        #         'client_id': settings.QQ_CLIENT_ID,
        #         'redirect_uri': settings.QQ_REDIRECT_URI,
        #         'state': state
        #     }
        #
        #     # 构建url
        #     qq_url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(data_dict)
        #
        #     # 返回url
        #     return Response({'login_url': qq_url})


# http://api.meiduo.site:8000/oauth/qq/user/?code=DED76AB1331A9B83F509D919D6826DCF
class QQAuthUserView(APIView):
    """
    QQ登录的用户
    """

    def get(self, request):
        # 获取code
        code = request.query_params.get('code')

        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        oauth_qq = OAuthQQ()

        try:
            # 凭借code 获取access_token
            access_token = oauth_qq.get_access_token(code)
            # 凭借access_token获取openid
            openid = oauth_qq.get_openid(access_token)
        except OAuthQQAPIError:
            return Response({'message': '访问QQ接口异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 凭借openid查询数据库OAuthQQUser 判断数据库是否存在
        try:
            oauth_qq_user = OAuthQQUser.objects.get(openid=openid)

        except OAuthQQUser.DoesNotExist:
            # 如果不存在，处理openid并返回
            access_token = oauth_qq.generate_bind_user_access_token(openid)
            return Response({'access_token':access_token})

        else:
            # 如果数据存在,表明用户已经绑定身份,签发JWT token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            user = oauth_qq_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response({
                'username':user.username,
                'user_id':user.id,
                'token':token
            })




















