from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU

"""
id	int	是	商品sku 编号
name	str	是	商品名称
price	decimal	是	单价
default_image_url	str	是	默认图片
comments	int	是	评论量
"""


class SKUSerializer(serializers.ModelSerializer):
    """
    SKU序列化器
    """

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')


class AddUserBrowsingHistorySerializer(serializers.Serializer):
    """
    添加用户浏览历史序列化器
    """
    sku_id = serializers.IntegerField(label='商品SKU编号', min_value=1)

    def validate_sku_id(self, value):
        """检查sku_id是否存在"""
        try:
            SKU.objects.get(id=value)
        except:
            raise serializers.ValidationError('该商品不存在')
        return value

    def create(self, validated_data):
        """保存"""
        # 获取用户id
        user_id = self.context['request'].user.id

        sku_id = validated_data['sku_id']

        # 建立缓存链接
        redis_conn = get_redis_connection('history')

        pl = redis_conn.pipeline()

        # 移除已存在的本商品的浏览记录
        pl.lrem('history_%s' % user_id, 0, sku_id)
        # 写入
        pl.lpush('history_%s' % user_id, sku_id)
        # 控制存存储的数量
        pl.ltrim('history_%s' % user_id, 0, 5)

        pl.execute()
        return validated_data
