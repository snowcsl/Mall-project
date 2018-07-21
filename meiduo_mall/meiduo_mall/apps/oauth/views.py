from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer
from oauth.utils import QAuthQQ


# Request URL:http://api.meiduo.site:8000/oauth/qq/authorization/?state=/
class QQAuthURLView(APIView):
    def get(self, request):
        # 获取state状态码
        state = request.query_params.get('state', settings.QQ_STATE)

        # 创建QQ对象
        qq = QAuthQQ(state=state)

        # 获取登录跳转的url
        qq_url = qq.get_qq_url()

        # 返回url
        return Response({'login_url': qq_url})


# http://www.meiduo.site:8080/oauth_callback.html?code=F1169431F7654DFA954FC7689F1231A7&state=%2F
class QQAuthUserView(APIView):
    """
    登陆QQ用户
    """

    def get(self, request):
        # 获取code参数
        code = request.query_params.get('code', None)

        if not code:
            return Response({'message': '缺少code值'}, status=status.HTTP_400_BAD_REQUEST)

        qq = QAuthQQ()

        try:
            # 获取access_token
            access_token = qq.get_access_token(code)

            # 获取openid
            openid = qq.get_open_id(access_token)

        except Exception as e:
            print(e)
            return Response({'message': 'qq服务器异常'}, status=status.HTTP_400_BAD_REQUEST)

        # 判断是否绑定通过
        qq_user = OAuthQQUser.objects.get(openid=openid)

        if not qq_user:

            # 用户未绑定返回加密后的openid

            tjs = TJS(settings.SECRET_KEY, 300)
            data = {'openid': openid}

            token = tjs.dumps(data).decode()

            return Response({'access_token': token})

        else:
            # 用户已经绑定 获取用户对象

            user = qq_user.user
            # 写入JWT
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response(
                {
                    'token': token,
                    'user_id': user.id,
                    'username': user.username
                }
            )

    def post(self, request):
        # 数据验证
        ser = OAuthQQUserSerializer(data=request.data)
        ser.is_valid()
        print(ser.errors)

        # 保存
        ser.save()

        # 返回数据
        return Response(ser.data)
