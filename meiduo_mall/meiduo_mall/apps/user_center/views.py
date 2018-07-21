from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user_center import serializers
from user_center.serializers import UserDetailViewSerializer


# Create your views here.
# class UserDetailView(APIView):
#     """
#     用户详情
#     """
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         # 获取用户对象
#         user = request.user
#         print(user)
#
#         # 返回数据
#         ser = UserDetailViewSerializer(user)
#
#         return Response(ser.data)
from users.models import User


class UserDetailView(RetrieveAPIView):
    """
    用户详情
    """
    serializer_class = serializers.UserDetailViewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# 保存用户的邮箱信息(注意需要用户登录通过认证后)
class EmailView(UpdateAPIView):
    """
    保存用户邮箱
    """
    permission_classes = [IsAuthenticated]

    serializer_class = serializers.EmailSerializer

    def get_object(self, *args, **kwargs):
        return self.request.user


# url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
class VerifyEmailView(APIView):
    """
    邮箱验证
    """
    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})

