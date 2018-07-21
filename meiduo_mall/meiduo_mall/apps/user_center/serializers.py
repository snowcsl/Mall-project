from rest_framework import serializers
from users.models import User
from celery_tasks.email.tasks import send_verify_email


class UserDetailViewSerializer(serializers.ModelSerializer):
    """
    用户详情序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


# 验证用户提交的邮箱信息
class EmailSerializer(serializers.ModelSerializer):
    """
    邮箱序列化器
    """
    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        """

        :param instance:  视图传过来的user对象
        :param validated_data:
        :return:
        """

        email = validated_data['email']

        instance.email = email
        instance.save()

        # 生成激活链接
        url = instance.generate_verify_email_url()

        # 发送邮件
        send_verify_email.delay(email, url)

        return instance