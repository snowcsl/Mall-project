from rest_framework import serializers
from .models import Area


class AreaSerializers(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name')


class SubAreaSerializers(serializers.ModelSerializer):
    sub = AreaSerializers(many=True,read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'name','subs')

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
