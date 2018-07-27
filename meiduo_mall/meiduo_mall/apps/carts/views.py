import base64
import pickle
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serializer import CartSerializer


class CartView(APIView):
    """
    购物车
    """
    def perform_authentication(self, request):
        pass

    def post(self,request):
        """
          获取前端数据 sku_id  count
        1.验证数据
        2.提取验证后的数据
        3.判断用户是否登陆
        4.用户已登录  数据保存在redis
        5.用户未登录  数据保存在cookie
            先判断有木有cookie数据
            判断数据是否存在,存在则累加
            加密处理
            写入cookie
        """

        # 1.验证数据
        ser=CartSerializer(data=request.data)
        ser.is_valid()
        print(ser.errors)

        # 2.提取验证后的数据
        sku_id=ser.validated_data['sku_id']
        count=ser.validated_data['count']
        selected=ser.validated_data['selected']

        # 3.判断用户是否登陆
        try:
            user=request.user
        except:
            user=None

        # 4.用户已登录  数据保存在redis
        if user is not None:

            conn=get_redis_connection('cart')

            # 数量关系存存储
            conn.hincrby('cart_%s'%user.id,sku_id,count)

            # 选中状态存储
            if selected:
                conn.sadd('cart_%s'%user.id,sku_id)

            return Response({'message':'ok'})

        # 用户未登录 数据保存在cookie
        else:
            # 先判断有木有cookie数据
            cart_cookie=request.COOKIES.get('cart_cookie')

            if cart_cookie:
                cart_dict=pickle.loads(base64.b64decode(cart_cookie.encode()))
            else:
                cart_dict={}

            # 判断数据是否存在,存在则累加
            sku_dict=cart_dict.get(sku_id,None)
            # 存在则累加
            if sku_dict:
                sku_dict['count'] += count

            # 不存在  组建新的数据字典
            cart_dict[sku_id]={
                'count':count,
                'selected':selected
            }

            # 加密处理
            cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 写入cookie
            response=Response({'message':'ok'})
            response.set_cookie('cart_cookie',cart_cookie,60*60*24*7)

            return response











