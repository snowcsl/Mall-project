from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """
    创建用户序列化器
    """
    password2 = serializers.CharField(max_length=20, min_length=8, write_only=True)
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    allow = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow')
        extra_kwargs = {
            'username': {
                'max_lenth': 20,
                'min_lenth': 5,
                'error_messages': {
                    'max_lenth': '名字过长',
                    'min_lenth': '名字过短',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    # 手机号判断
    def validate_mobile(self, value):
        if value != 'true':
            raise serializers.ValidationError('手机号不符合要求')

        return value

    # 协议判断
    def validate_allow(self, value):
        if value != 'true':
            raise serializers.ValidationError('请统一协议')

        return value

    # 多个字段判断
    def validate(self, attrs):

        # 密码对比
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('密码不一致')

        # 短信验证码
        # 获取缓存中的验证码
        conn = get_redis_connection('verify_codes')

        real_sms_code = conn.get('sms_code_%s' % attrs['mobile'])

        if not real_sms_code:
            raise serializers.ValidationError('验证码失效')

        real_sms_code = real_sms_code.decode()

        if attrs['sms_code'] != real_sms_code:
            raise serializers.ValidationError('验证码错误')

        return attrs

    def create(self, validated_data):

        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        user = super().create(validated_data)

        user.set_password(validated_data['password'])
        user.save()

        return user
