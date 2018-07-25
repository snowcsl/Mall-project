from django.shortcuts import render
from rest_framework.generics import ListAPIView,GenericAPIView
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from goods.models import SKU

# Create your views here.

from goods.serializers import SKUSerializer


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


class HotSKUListView(ListAPIView):
    """
    热销商品, 使用缓存扩展
    """
    serializer_class = SKUSerializer

    def get_queryset(self):

        category_id=self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')[:5]


