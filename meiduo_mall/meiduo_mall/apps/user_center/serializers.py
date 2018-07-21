from rest_framework import serializers
from users.models import User


class UserDetailViewSerializer(serializers.ModelSerializer):
    """
    用户详情序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')
