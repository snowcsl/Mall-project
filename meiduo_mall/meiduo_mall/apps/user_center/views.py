from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView
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
