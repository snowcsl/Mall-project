from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from users.models import User
from users.serializers import CreateUserSerializer


# Create your views here.

# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """
    用户名数量
    """

    def get(self, request, username):
        # 获取用户名数据对象的数量

        count = User.objects.filter(username=username).count()

        # 返回数量

        return Response(
            {
                'count': count,
                'username': username,
            }
        )


class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        # 获取手机号数据对象的数量
        count = User.objects.filter(mobile=mobile).count()

        # 返回数量
        return Response(
            {
                'count': count,
                'mobile': mobile,
            }
        )


# url(r'^users/$', views.UserView.as_view()),
class UserView(CreateAPIView):
    """
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    """
    serializer_class = CreateUserSerializer
