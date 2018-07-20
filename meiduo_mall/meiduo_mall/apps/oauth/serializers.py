import re
from django.conf import settings
from django_redis import get_redis_connection
from rest_framework import serializers
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthQQUser
from users.models import User

'''
mobile	str	是	手机号
password	str	是	密码
sms_code	str	是	短信验证码
access_token	str	是	凭据 （包含openi

'''


class OAuthQQUserSerializer(serializers.ModelSerializer):
    """
    保存QQ用户序列化器
    """
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    access_token = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('mobile', 'password', 'sms_code', 'access_token', 'id', 'username', 'token')

        extra_kwargs = {
            'username': {
                'read_only': True
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
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号不符合要求')

        return value

    # 多字段判断
    def validate(self, attrs):

        #  access_token 解密
        tjs = TJS(settings.SECRET_KEY, 300)

        try:
            data = tjs.loads(attrs['access_token'])
        except:
            raise serializers.ValidationError('无效的access_token')

        # 提取openid
        openid = data.get('openid', None)
        if not openid:
            raise serializers.ValidationError('获取openid失败')
        # 添加openid
        attrs['openid'] = openid

        # 短信验证码
        # 获取缓存中的短信
        conn = get_redis_connection('verify_codes')

        real_sms_code = conn.get('sms_code_%s' % attrs['mobile'])

        if not real_sms_code:
            raise serializers.ValidationError('验证码失效')

        real_sms_code = real_sms_code.decode()

        if attrs['sms_code'] != real_sms_code:
            raise serializers.ValidationError('验证码错误')

        # 判断用户
        try:
            user = User.objects.get(mobile=attrs['mobile'])
        except:
            user = None

        if user is not None and user.check_password(attrs['password']):
            attrs['user'] = user

        return attrs

    def create(self, validated_data):

        user = validated_data.get('user', None)
        if not user:
            # 未注册用户
            # 先注册用户
            user = User.objects.create_user(username=validated_data['mobile'], mobile=validated_data['mobile'],
                                            password=validated_data['password'])

        # 进行绑定
        OAuthQQUser.objects.create(user=user, openid=validated_data['openid'])

        # 生成jwt token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user
