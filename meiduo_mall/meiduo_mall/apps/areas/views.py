from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.models import Area
from . import serializers


# Create your views here.
# class AreasViewSet(ListModelMixin,RetrieveModelMixin,GenericAPIView)
class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    # class ReadOnlyModelViewSet(mixins.RetrieveModelMixin,
    #                            mixins.ListModelMixin,
    #                            GenericViewSet):
    #     """
    #     A viewset that provides default `list()` and `retrieve()` actions.
    #     """
    #     pass

    # 关闭分页处理
    pagination_class = None

    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.SubAreaSerializers
        else:
            return serializers.SubAreaSerializers
