from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from goods.models import SKU
from goods.serializers import SKUSerializer, AddUserBrowsingHistorySerializer

# Create your views here.
# class HotSKUListView(GenericAPIView):
#     """
#     热销商品, 使用缓存扩展
#     """
#     serializer_class = SKUSerializer
#
#     def get(self, request, category_id):
#         hot_skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:5]
#         ser = self.get_serializer(hot_skus, many=True)
#         return Response(ser.data)
from meiduo_mall.utils.pagination import StandardResultsSetPagination


class HotSKUListView(ListAPIView):
    """
    热销商品, 使用缓存扩展
    """
    serializer_class = SKUSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:5]


class UserBrowsingHistoryView(CreateAPIView):
    """
    用户浏览历史记录
    """
    serializer_class = AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 从缓存中获取数据id
        conn = get_redis_connection('history')
        skus = conn.lrange('history_%s' % request.user.id, 0, 5)

        sku_list = []
        # 遍历取出sku对象
        for sku_id in skus:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)
        ser = SKUSerializer(sku_list, many=True)

        return Response(ser.data)


class SKUListView(ListAPIView):
    """
    sku列表数据
    """
    serializer_class = SKUSerializer

    pagination_class = StandardResultsSetPagination

    filter_backends = [OrderingFilter]
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)
