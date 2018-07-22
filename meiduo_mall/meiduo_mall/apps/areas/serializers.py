from rest_framework import serializers

from .models import Area


class AreaSerializer(serializers.ModelSerializer):
    """
    行政区划信息序列化器
    """
    class Meta:
        model = Area
        fields = ('id', 'name')


# class SubAreaSerializer(serializers.ModelSerializer):
#     """
#     子行政区划信息序列化器
#     """
#     subs = AreaSerializer(many=True, read_only=True)  # 关联嵌套序列化
#
#     class Meta:
#         model = Area
#         fields = ('id', 'name', 'subs')  # subs 反向引用

        # 如:
        # {
        #     "id": "110100",
        #     "name": "北京市",
        #     "subs": [
        #         {
        #             "id": "110101",
        #             "name": "东城区"
        #         }
        # }
