from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from oauth.utils import OAuthQQ
# Create your views here.


#  url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
class QQAuthURLView(APIView):
    """
    获取Q登陆的url地址  ?next=xxx

    """
    def get(self,request):
        # 获取next参数
        next= request.query_params.get('next')

        # 拼接QQ登录的地址
        oauth_qq =  OAuthQQ(state=next)
        login_url = oauth_qq.get_qq_login_url()

        # 返回
        return Response({'login_url':login_url})
