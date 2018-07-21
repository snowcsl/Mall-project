from django.shortcuts import render
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