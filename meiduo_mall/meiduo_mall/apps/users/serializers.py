from rest_framework import serializers
from rest_framework.settings import api_settings

from users.models import User
from django_redis import get_redis_connection
import re


class CreateUserSerializer(serializers.ModelSerializer):
    """
    创建用户序列化器
    """
    # 对额外的字段进行指定
    password2 = serializers.CharField(max_length=20, min_length=8, write_only=True)
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    allow = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # 指定那些字段生成序列化器字段
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow')
        # 对一些参数进行额外属性的添加
        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5,
                'error_messages': {
                    'max_length': '名字太长',
                    'min_length': '名字太短'
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

    # 以上是对一些字段的基本验证,下面是复杂验证(对单一字段的验证 & 对复杂字段的验证)

    # 手机号判断
    def validate_mobile(self, value):

        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号不符合要求')

        return value

    # 协议判断
    def validate_allow(self, value):

        if value != 'true':
            raise serializers.ValidationError('请同意协议')

        return value

    # 多个字段判断
    def validate(self, attrs):

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('密码不一致')

        # 短信验证码
        # 获取缓存中的短信
        conn = get_redis_connection('verify_codes')  # 建立连接

        real_sms_code = conn.get('sms_code_%s' % attrs['mobile'])  # 怎么存的就怎么取

        if not real_sms_code:
            raise serializers.ValidationError('验证码失效')

        real_sms_code = real_sms_code.decode()  # 从数据库获取的是bytes类型,需要转化为字符串

        if attrs['sms_code'] != real_sms_code:
            raise serializers.ValidationError('验证码错误')

        return attrs

    def create(self, validated_data):
        """
        反序列化过程中的保存过程
        ModelSerializer自动生成字段,相应的方法已经写好
        由于验证的过程中一些字段不需要保存,需要重写create方法,先删除不需要保存的字段

        """
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        user = super().create(validated_data)  # 调用父类的方法把删除后的字段传进去,保存后返回一个用户对象

        user.set_password(validated_data['password'])
        user.save()

        # 签发jwt token  生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token

        return user

        # 对于 create &　update保存后返回的是一个对象,validate返回的是一个是一个数据
        # 序列化器中实现数据保存和数据返回的过程
