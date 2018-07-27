
from rest_framework.views import APIView
from rest_framework.response import Response
from django_redis import get_redis_connection
import pickle,base64

from carts.serializers import CartSerializer


class CartView(APIView):
    """
    购物车
    """
    def perform_authentication(self, request):
        pass

    def post(self,request):

        # 验证数据
        ser=CartSerializer(data=request.data)
        ser.is_valid()
        print(ser.errors)

        # 提取验证后的数据
        sku_id=ser.validated_data.get('sku_id')
        count=ser.validated_data.get('count')
        selected=ser.validated_data.get('selected')

        # 判断用户是否登录
        try:
            user=request.user
        except:
            user=None

        if user is not None:
            # 用户已登录  数据保存在redis
            conn=get_redis_connection('cart')

            # HINCRBY()
            # 用户已登录  数据保存在redis
            conn.hincrby('cart_%s'%user.id,sku_id,count)
            # 选中状态存储
            if selected:
                conn.sadd('cart_select_%s'%user.id,sku_id)
            return Response({'message':'ok'})

        else:
            # 用户未登录  数据保存在cookie
            # 先判断有木有cookie数据
            cart_cookie=request.COOKIES.get('cart_cookie')
            if cart_cookie:
                cart_dict=pickle.loads(base64.b64decode(cart_cookie.encode()))
            else:
                cart_dict={}


            '''
                {
                    sku_id: {
                        "count": xxx,  // 数量
                        "selected": True  // 是否勾选
                    },
                    sku_id: {
                        "count": xxx,
                        "selected": False
                    },
                    ...
                }
            
            '''
            # 判断数据是否存在,存在则累加
            sku_dict=cart_dict.get(sku_id,None)
            if  sku_dict:
                sku_dict['count']+=count

            cart_dict[sku_id]={
                'count':count,
                'selected':selected
            }

            # 加密处理
            cart_cookie=base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 写入cookie
            response=Response({'message':'ok'})

            response.set_cookie('cart_cookie',cart_cookie,60*60*24*7)


            return response