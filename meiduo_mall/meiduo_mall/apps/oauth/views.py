from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS

from carts.utils import merge_cart_cookie_to_redis
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer
from oauth.utils import OAuthQQ


# Create your views here.
class QQAuthURLView(APIView):
    """
    获取QQ登录的url
    """

    def get(self, request):
        # 获取state
        state = request.query_params.get('state', settings.QQ_STATE)

        # 创建qq对象
        qq = OAuthQQ(state=state)

        # 获取登录跳转的url
        qq_url = qq.get_qq_url()

        # 返回url
        return Response({'login_url': qq_url})


# http://api.meiduo.site:8000/oauth/qq/user/?code=DED76AB1331A9B83F509D919D6826DCF
class QQAuthUserView(APIView):
    """
    QQ登录的用户
    """

    def get(self, request):
        # 获取code参数
        code = request.query_params.get('code', None)

        if not code:
            return Response({'message': '缺少code值'}, status=status.HTTP_400_BAD_REQUEST)

        qq = OAuthQQ()
        try:
            # 获取access_token值
            access_token = qq.get_access_token(code)
            # 获取open_id值
            openid = qq.get_open_id(access_token)
        except Exception as e:
            print(e)
            return Response({'message': 'qq服务器异常'}, status=status.HTTP_400_BAD_REQUEST)

        # 判断是否绑定过openid
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except:
            qq_user = None

        if not qq_user:
            # 用户未绑定
            # 返回加密后的openid数据
            tjs = TJS(settings.SECRET_KEY, 300)
            data = {'openid': openid}
            token = tjs.dumps(data).decode()
            return Response({'access_token': token})

        else:
            # 用户已绑定
            # 获取用户对象
            user = qq_user.user
            # 写入jwt
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response(
                {
                    'token': token,
                    'user_id': user.id,
                    'username': user.username
                }
            )

            response = merge_cart_cookie_to_redis(request, user, response)

            return response

    def post(self, request):

        # 数据验证
        ser = OAuthQQUserSerializer(data=request.data)
        ser.is_valid()
        print(ser.errors)
        user = ser.validated_data['user']

        # 保存
        ser.save()
        response = Response(ser.data)
        response = merge_cart_cookie_to_redis(request, response, user)
        return response
