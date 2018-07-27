import base64
import pickle
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import response
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serializer import CartSerializer, CartSKUSerializer, CartDeleteSerializer
from goods.models import SKU


class CartView(APIView):
    """
    购物车
    """

    def perform_authentication(self, request):
        pass

    def post(self, request):
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
        ser = CartSerializer(data=request.data)
        ser.is_valid()
        print(ser.errors)

        # 2.提取验证后的数据
        sku_id = ser.validated_data['sku_id']
        count = ser.validated_data['count']
        selected = ser.validated_data['selected']

        # 3.判断用户是否登陆
        try:
            user = request.user
        except:
            user = None

        # 4.用户已登录  数据保存在redis
        if user is not None:

            conn = get_redis_connection('cart')

            # 数量关系存存储
            conn.hincrby('cart_%s' % user.id, sku_id, count)

            # 选中状态存储
            if selected:
                conn.sadd('cart_%s' % user.id, sku_id)

            return Response({'message': 'ok'})

        # 用户未登录 数据保存在cookie
        else:
            # 先判断有木有cookie数据
            cart_cookie = request.COOKIES.get('cart_cookie')  # 先设定存储的key值为cart_cookie

            if cart_cookie:  # cookie数据存在： 解密；获取的cookie数据是字符串形式，encode()后转化为字典
                cart_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))
            else:
                cart_dict = {}

            # 判断数据是否存在,存在则累加
            sku_dict = cart_dict.get(sku_id, None)

            # 存在则累加
            if sku_dict:
                # sku_dict['count'] += count
                data = int(sku_dict['count'])
                data += count
                sku_dict['count'] = data

            # 不存在  组建新的数据字典
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 加密处理
            cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 写入cookie
            response = Response({'message': 'ok'})
            response.set_cookie('cart_cookie', cart_cookie, 60 * 60 * 24 * 7)

            return response

    def get(self, request):
        """
        # 1.判断用户是否存在
        # 2.如果用户已经登录，从Redis中获取数据
            # 提取数量数据
            # 选中状态
            # 把数量数据和选中状态整合在一个字典中
        # 3.如果用户未登录，从cookie中获取数据
            # 先判断有没有cookie值，如果有先解密
        # 4.获取所有的数据对象
        # 5.添加属性
        # 6.序列化数据
        # 7.返回数据

        :param request:
        :return:
        """
        # 1. 判断用户是否存在
        try:
            user = request.user
        except:
            user = None

        if user is not None:
            # 2. 如果用户已经登录，从Redis中获取数据
            conn = get_redis_connection('cart')

            # 提取数量数据  字典数据
            cart_count = conn.hgetall('cart_%s' % user.id)
            # 获取选中状态的商品的所有数据  列表数据
            cart_selected = conn.smembers('cart_select_%s' % user.id)

            # 把数量数据和选中状态整合在一个字典中
            cart = {}

            for sku_id, count in cart_count.items():  # items()将key值和value值分别取出来给赋值给sku_id,count

                cart[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                    # selected的取值是通过判断sku_id是否在cart_selected这个集合中，如果在返回True,不在返回False
                }

        else:
            # 3.如果用户未登录，从cookie中获取数据
            cart_cookie = request.COOKIES.get('cart_cookie')

            if cart_cookie:  # 如果cookie中有数据，解密cart_cookie
                cart = pickle.loads(base64.b64decode(cart_cookie.encode()))
            else:
                cart = {}

        # 对登录者为登录的数据(此时已经统一为了字典形式)进行处理(数据提取)

        # 4. 获取所有的数据对象
        # keys()查询字典中所有的key值，这里值所有的sku_id,  id_in=表示id在..范围之内
        # 从数据库中进行过滤查询，如果id在这个范围内进行返回
        skus = SKU.objects.filter(id__in=cart.keys())

        # 添加属性:由于在对象中没有count&selected这两个属性，在返回之前先添加属性
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        # 序列化数据
        ser = CartSKUSerializer(skus, many=True)

        # 返回数据
        return Response(ser.data)

    def put(self, request):
        """
        1.获取数据
        2.验证shuju
        3.提取验证后的数据
        4.判断用户是否登录
        5.如果用户已经登录，从Redis中获取数据，更新数量关系和选中状态
        6.如果用户未登录，从cookie中获取数据，
        先判断是否存在数据，存在数据再解密，数据更新，加密，写入cookie
        7.返回Response
        :param request:
        :return:
        """
        # 验证数据
        ser = CartSerializer(data=request.data)
        ser.is_valid()
        print(ser.errors)

        # 提取验证后的数据
        sku_id = ser.validated_data.get('sku_id')
        count = ser.validated_data.get('count')
        selected = ser.validated_data.get('selected')

        # 判断用户是否登录
        try:
            user = request.user
        except:
            user = None

        if user is not None:
            # 如果用户已经登录，从Redis中获取数据
            conn = get_redis_connection('cart')

            # 更新数量关系
            conn.hset('cart_%s' % user.id, sku_id, count)

            # 更新选中状态
            if selected:
                conn.sadd('cart_select_%s' % user.id, sku_id)
            else:
                conn.srem('cart_select_%s' % user.id, sku_id)

            return Response(ser.data)

        else:
            # 如果用户未登录，从cookie中获取数据
            # 先判断是否存在cookie
            cart_cookie = request.COOKIES.get('cart_cookie')
            if cart_cookie:
                cart_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))
            else:
                cart_dict = {}

            # 数据更新
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 加密处理
            cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()

            response = Response(ser.data)

            # 写入cookie
            response.set_cookie('cart_cookie', cart_cookie, 60 * 60 * 24 * 7)

            return response

    def delete(self, request):
        """
        1.获取数据
        2.验证数据
        3.提取验证后的数据
        4.判断用户是否登录
        5.如果用户已经登录，从redis中获取数据，删除数量关系或者删除选中状态，返回状态
        6.用户未登录，从cookie中获取数据，如果存在数据，解密，判断数据并删除，加密处理，写入cookie,并返回状态
        :param request:
        :return:
        """

        # 验证数据
        ser = CartDeleteSerializer(data=request.data)
        ser.is_valid()
        print(ser.errors)

        # 提取验证后的数据
        sku_id = ser.validated_data['sku_id']

        # 判断用户是否登录
        try:
            user = request.user
        except:
            user = None

        if user is not None:
            # 如果用户已经登录，从Redis中获取数据
            conn = get_redis_connection('cart')

            # 删除数量关系
            conn.hdel('cart_%s' % user.id, sku_id)
            # 删除选中状态
            conn.srem('cart_select_%s' % user.id, sku_id)

            return Response(status=200)

        else:
            # 用户未登录  数据保存在cookie
            # 先判断有木有cookie数据
            cart_cookie = request.COOKIES.get('cart_cookie')

            if cart_cookie:

                cart_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))

                if sku_id in cart_dict:
                    del cart_dict[sku_id]

                # 加密处理
                cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode() # b64encode  decode

            response = Response(status=200)

            # 写入cookie
            response.set_cookie('cart_cookie', cart_cookie, 60 * 60 * 24 * 7)

            return response
