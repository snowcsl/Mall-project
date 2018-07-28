from django.db import transaction
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


class SaveOrderSerializer(serializers.ModelSerializer):
    """
    下单数据序列化器
    """

    class Meta:
        model = OrderInfo
        fields=('order_id', 'address', 'pay_method')
        extra_kwargs={
            'order_id':{
                'read_only':True
            },
            'address':{
                'write_only':True,
                'required':True,
            },
            'pay_method':{
                'write_only':True,
                'required':True,
            }
        }

    def create(self, validated_data):
        """
        1.获取用户对象
        2.获取验证后的数据
        3.生成订单编号
        4.生成订单基本信息表
        5.获取缓存中的商品信息 生成商品信息表
            5.1 判断库存
            5.2 更新库存和销量
            5.3 生成商品订单表
        6.删除缓存中的商品信息

        """

        # 1.获取用户对象
        # 2.获取验证后的数据
        # 3.生成订单编号
        with transaction.atomic():
            # 创建保存点
            save_point=transaction.savepoint()

            # 4.生成订单基本信息表
            # 5.获取缓存中的商品信息 生成商品信息表
            #     5.1 判断库存
            #     5.2 更新库存和销量
            #     5.3 生成商品订单表
        # 回滚到保存点
        transaction.savepoint_rollback(save_point)

        # 提交从保存点到当前状态的所有数据库事务操作
        transaction.savepoint_commit(save_point)

        # 6.删除缓存中的商品信息
























