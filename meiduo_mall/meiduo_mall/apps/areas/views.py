from rest_framework.generics import ListAPIView

from areas.models import Area
from areas.serializers import AreaSerializer


# from areas.serializers import AreaSerializer, SubAreaSerializer
# from rest_framework.viewsets import ReadOnlyModelViewSet
# from .models import Area


# Create your views here.
# 实现方式1
class AreasView(ListAPIView):  # 获取省
    serializer_class = AreaSerializer  # 过滤省的信息
    queryset = Area.objects.filter(parent=None)


class AreaView(ListAPIView):  # 获取单一数据，但返回的是多条数据信息 使用ListAPIView
    serializer_class = AreaSerializer
    # queryset = Area.objects.filter(parent_id=id)  # id值无法直接从查询集中获取到，可以在方法中获取id值

    def get_queryset(self):   # get_queryset()对查询集结果进行返回，可以自行指定返回的结果
        id = self.kwargs['pk']  # kwargs 是正则匹配的pk值,如果没有指定lookup_field=id，则匹配pk值
        return Area.objects.filter(parent_id=id)


# 实现方式2
# class AreasViewSet(ListModelMixin,RetrieveModelMixin,GenericAPIView)
# class AreasViewSet(ReadOnlyModelViewSet):
#     """
#     行政区划信息
#     """
#     pagination_class = None  # 区划信息不分页
#
#     def get_queryset(self):
#         """
#         提供数据集
#         """
#         if self.action == 'list':
#             return Area.objects.filter(parent=None)
#         else:
#             return Area.objects.all()
#
#     def get_serializer_class(self):
#         """
#         提供序列化器
#         """
#         if self.action == 'list':
#             return AreaSerializer
#         else:
#             return SubAreaSerializer
