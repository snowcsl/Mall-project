from rest_framework import serializers

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """
    购物车数据序列化器
    """
    sku_id=serializers.IntegerField(min_value=1)
    count=serializers.IntegerField(min_value=1)
    selected=serializers.BooleanField(default=True)

    def validate(self, attrs):
        try:
            sku=SKU.objects.get(id=attrs['sku_id'])
        except:
            raise serializers.ValidationError('sku_id errors!!!')

        if sku.stock < attrs['count']:
            raise serializers.ValidationError('库存量不足')

        return attrs


class CartSKUSerializer(serializers.ModelSerializer):
    """
       购物车商品数据序列化器
       """
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price', 'selected')