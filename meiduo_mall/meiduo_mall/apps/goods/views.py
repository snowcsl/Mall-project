from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from goods.models import SKU

# Create your views here.

from goods.serializers import SKUSerializer


class HotSKUListView(ListAPIView):
    """
    热销商品, 使用缓存扩展
    """
    serializer_class = SKUSerializer

    def get_queryset(self):
        category_id=self.kwargs['category_id ']
        hot_sku=SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sale')[:5]
        return hot_sku

