from decimal import Decimal
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serialziers import OrderSettlementSerializer, SaveOrderSerializer


class OrderSettlementView(APIView):
    """
    订单结算
    """

    def get(self, request):

        # 从缓存中获取数据
        conn = get_redis_connection('cart')

        # 获取数量关系
        cart_count = conn.hgetall('cart_%s' % request.user.id)

        # 获取选中状态
        cart_seleted = conn.smembers('cart_select_%s' % request.user.id)

        # 提取选中状态的数据写入到一个新字典中
        cart = {}
        for sku_id in cart_seleted:
            cart[int(sku_id)] = int(cart_count[sku_id])

        # 获取商品数据对象
        skus = SKU.objects.filter(id__in=cart.keys())

        # 增加count属性
        for sku in skus:
            sku.count = cart[sku.id]
        freight = Decimal('10.00')

        # 序列化处理
        ser = OrderSettlementSerializer({'skus': skus, 'freight': freight})

        # 返回状态
        return Response(ser.data)


class SaveOrderView(CreateAPIView):
    """
    保存订单
    """
    # def post(self, request, *args, **kwargs):
    #     pass
        # 获取前端数据
        # 验证数据
        # 保存数据
        # 结果返回
    serializer_class = SaveOrderSerializer
