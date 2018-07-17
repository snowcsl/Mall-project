from rest_framework import serializers

from django_redis import get_redis_connection


class ImageCodeCheckSerializer(serializers.Serializer):
    """
    图片验证码校验序列化器
    """
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        # 获取验证数据
        text = attrs['text']
        image_code_id = attrs['image_code_id']

        # 获取缓存中的验证码
        conn = get_redis_connection('verify_codes')
        real_text = conn.get('img_%s' % image_code_id)
        if not real_text:
            raise serializers.ValidationError('验证码失效')

        # 删除验证码
        conn.delete('img_%s' % image_code_id)

        # 验证码比对
        if text.lower() != real_text.decode().lower():
            raise serializers.ValidationError('验证码错误')

        # 判断短信验证码的时间
        mobile = self.context['view'].kwargs['mobile']
        flag = conn.get('sms_flag_%s' % mobile)
        if flag:
            raise serializers.ValidationError('操作过于频繁')

        return attrs
