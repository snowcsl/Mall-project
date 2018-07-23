import re

from rest_framework import serializers
from users.models import User, Address
from celery_tasks.email.tasks import send_verify_email


class UserDetailViewSerializer(serializers.ModelSerializer):
    """
    用户详情序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


# 验证用户提交的邮箱信息   保存的过程中发送链接
class EmailSerializer(serializers.ModelSerializer):  # 邮箱存在于用户模型类中，选择ModelSerializer
    """
    邮箱序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True # 必须传过来一个email值，模型类指定的字段类型是null
            }
        }

    def update(self, instance, validated_data):
        """

        :param instance:  视图传过来的需要更新的user对象
        :param validated_data:
        :return:
        """

        email = validated_data['email']

        instance.email = email
        instance.save()

        # 生成激活链接
        url = instance.generate_verify_email_url()

        # 发送邮件 --> 数据保存的时候发送邮件
        send_verify_email.delay(email, url)

        return instance
        # 数据返回时根据关联性进行返回，如果不确定的话，返回出密码之外所有的数据


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)    # required是限制必须写的字段
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """
        保存
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """

    class Meta:
        model = Address
        fields = ('title',)
