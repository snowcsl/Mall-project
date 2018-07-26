from django_redis import get_redis_connection
from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers

from goods.models import SKU
from goods.search_indexes import SKUIndex

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
    sku_id = serializers.IntegerField(label="商品SKU编号", min_value=1)

    def validate_sku_id(self, value):
        """
        检验sku_id是否存在
        """
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('该商品不存在')
        return value

    def create(self, validated_data):

        # 获取用户id值
        id = self.context['request'].user.id

        # 建立缓存链接
        conn = get_redis_connection('history')
        # 数据保存  列表形式  集合
        # 通过删除的形式来判断重复数据
        pl = conn.pipeline()
        pl.lrem('history_%s' % id, 0, validated_data['sku_id'])
        # 写入
        pl.lpush('history_%s' % id, validated_data['sku_id'])
        # 控制存储数量
        pl.ltrim('history_%s' % id, 0, 5)

        pl.execute()

        # 返回
        return validated_data


class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object=SKUSerializer(read_only=True)
    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')