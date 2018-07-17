from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from django_redis import get_redis_connection
from django.http import HttpResponse
from rest_framework.response import Response

from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.libs.yuntongxun.sms import CCP
from verifications.content import IMAGE_CODE_REDIS_EXPIRES, SMS_CODE_REDIS_EXPIRES, SEND_SMS_CODE_INTERVAL
from verifications.serializers import ImageCodeCheckSerializer
from random import randint


# Create your views here.
class ImageCodeView(APIView):
    """
    图片验证码
    """

    def get(self, request, image_code_id):
        # 生成图片验证码
        text, image = captcha.generate_captcha()
        # 写入缓存
        conn = get_redis_connection('verify_codes')
        conn.setex('img_%s' % image_code_id, IMAGE_CODE_REDIS_EXPIRES, text)

        # 返回图片验证码
        return HttpResponse(image, content_type='images/jpg')


# url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(GenericAPIView):
    """
    短信验证码
    传入参数：
        mobile, image_code_id, text
    """
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):
        # 获取前端数据进行验证
        ser = self.get_serializer(data=request.query_params)
        ser.is_valid()

        # print(self.kwargs['mobile'])

        # 生成短信验证码
        sms_code = '%06d' % randint(0, 999999)

        # 判断短信验证码的时间

        # 将短信验证码写入缓存
        conn = get_redis_connection('verify_codes')
        pl = conn.pipeline()
        pl.setex('sms_%s' % mobile, SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('sms_flag_%s' % mobile, SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # 发送短信给验证码
        sms_code_exprice = str(SMS_CODE_REDIS_EXPIRES // 60)
        ccp = CCP()
        ccp.send_template_sms(mobile, [sms_code, sms_code_exprice], 1)

        return Response({'message': 'ok'})
