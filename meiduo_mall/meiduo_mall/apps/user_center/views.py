from django.shortcuts import render
from rest_framework import mixins
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from users.models import User
from user_center import constants
from user_center import serializers
from user_center.serializers import UserDetailViewSerializer
from rest_framework.decorators import action


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

    def get_object(self, *args, **kwargs):  # get_object获取用户对象需要id值，但没有，重写
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
        user = User.check_verify_email_token(token)  # 加密 & 用户查询

        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True  # 状态更新
            user.save()
            return Response({'message': 'OK'})


# 用户地址新增与修改
class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = serializers.UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_delete=False)

    # GET/addresses
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()  # 查询集
        serializers = self.get_serializer(queryset, many=True)
        user=self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })


















