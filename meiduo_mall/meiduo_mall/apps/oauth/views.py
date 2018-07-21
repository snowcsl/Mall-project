from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
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
