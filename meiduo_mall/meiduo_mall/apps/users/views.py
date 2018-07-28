from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from carts.utils import merge_cart_cookie_to_redis
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


from rest_framework_jwt.views import ObtainJSONWebToken


class UserAuthorizeView(ObtainJSONWebToken):
    """
    用户认证
    """

    def post(self, request, *args, **kwargs):
        # 调用父类的方法，获取drf jwt扩展默认的认证用户处理结果
        response = super().post(request, *args, **kwargs)

        # 仿照drf jwt扩展对于用户登录的认证方式，判断用户是否认证登录成功
        # 如果用户登录认证成功，则合并购物车
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            response = merge_cart_cookie_to_redis(request, user, response)

        return response
