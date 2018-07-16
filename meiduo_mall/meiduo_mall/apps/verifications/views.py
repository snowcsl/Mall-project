from django.http import HttpResponse
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.response import Response

from meiduo_mall.libs.captcha.captcha import captcha
from verifications.content import IMAGE_CODE_REDIS_EXPIRES


# Create your views here.
class ImageCodeView(APIView):
    """
    图片验证码
    """

    def get(self, request, image_code_id):
        # 获取UUID
        # 生成图片验证码
        text,image = captcha.generate_captcha()
        # 写入缓存
        conn = get_redis_connection('verify_codes')
        conn.setex('img_%s' % image_code_id,IMAGE_CODE_REDIS_EXPIRES,text)
        # 返回图片验证码
        return HttpResponse(image,content_type='images/jpg')
