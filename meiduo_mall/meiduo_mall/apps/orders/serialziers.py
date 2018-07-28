from datetime import datetime

from decimal import Decimal
from django.db import transaction
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


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
        fields = ('order_id', 'address', 'pay_method')
        extra_kwargs = {
            'order_id': {
                'read_only': True
            },
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True,
            }
        }

    # def create(self, validated_data):
    #     """
    #     1.获取用户对象
    #     2.获取验证后的数据
    #     3.生成订单编号
    #     4.生成订单基本信息表
    #     5.获取缓存中的商品信息 生成商品信息表
    #         5.1 判断库存
    #         5.2 更新库存和销量
    #         5.3 生成商品订单表
    #     6.删除缓存中的商品信息
    #
    #     """
    #
    #     # 1.获取用户对象
    #     user = self.context['request'].user
    #
    #     # 2.获取验证后的数据
    #     address = validated_data['address']
    #     pay_method = validated_data['pay_method']
    #
    #     # 3.生成订单编号
    #     order_id = datetime.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id
    #
    #     with transaction.atomic():
    #         # 创建保存点
    #         save_point = transaction.savepoint()
    #         try:
    #             # 4.生成订单基本信息表
    #             order = OrderInfo.objects.create(
    #                 order_id=order_id,
    #                 user=user,
    #                 total_count=0,
    #                 address=address,
    #                 total_amount=Decimal(0),
    #                 freight=Decimal(0),
    #                 pay_method=pay_method,
    #                 status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
    #                     'CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID']
    #             )
    #             # 5.获取缓存中的商品信息 生成商品信息表
    #             # 从缓存中获取数据
    #             conn = get_redis_connection('cart')
    #
    #             # 获取数量关系
    #             cart_count = conn.hgetall('cart_%s' % user.id)
    #             # 获取选中状态
    #             cart_selected = conn.smembers('cart_select_%s' % user.id)
    #
    #             # 提取选中状态的数据写入到一个新字典中
    #             cart = {}
    #             for sku_id in cart_selected:
    #                 cart[int(sku_id)] = int(cart_count[sku_id])
    #
    #             # # 获取选中状态商品数据对象
    #             # skus = SKU.objects.filter(id__in=cart.keys())
    #
    #             for sku_id in cart.keys():
    #                 while True:
    #                     sku = SKU.objects.get(id=sku_id)
    #                     sku_count = cart[sku.id]  # 当前商品所需要购买的数量
    #
    #                     old_stock = sku.stock
    #                     old_sales = sku.sales
    #
    #                     # 5.1 判断库存
    #                     if sku_count > old_stock:
    #                         raise serializers.ValidationError('库存不足')
    #
    #                     # 5.2 更新库存和销量  sku表  spu表
    #                     new_stock = sku.stock - sku_count
    #                     new_sales = sku.sales + sku_count
    #
    #                     ret = SKU.objects.filter(stock=old_stock, id=sku_id).update(sales=new_sales, stock=new_stock)
    #                     if ret == 0:
    #                         continue
    #
    #                     sku.goods.sales += sku_count
    #                     sku.goods.save()
    #
    #                     # 更新orderinfo表
    #                     order.total_amount += (sku.price * sku_count)
    #                     order.total_count += sku_count
    #
    #                     # 5.3 生成商品订单表
    #                     OrderGoods.objects.create(
    #                         order=order,
    #                         sku=sku,
    #                         count=sku_count,
    #                         price=sku.price
    #
    #                     )
    #
    #             # 总价累加运费
    #             order.total_amount += order.freight
    #             order.save()
    #
    #         except Exception as e:
    #             print(e)
    #
    #             # 回滚到保存点
    #             transaction.savepoint_rollback(save_point)
    #             raise serializers.ValidationError('error')
    #         else:
    #             # 提交从保存点到当前状态的所有数据库事务操作
    #             transaction.savepoint_commit(save_point)
    #
    #             # 6.删除缓存中的商品信息
    #             conn.hdel('cart_%s' % user.id, *cart_selected)
    #             conn.srem('cart_select_%s' % user.id, *cart_selected)
    #
    #             return order

    def create(self, validated_data):

        # 获取用户对象
        user = self.context['request'].user

        # 获取验证后的数据
        address = validated_data['address']
        pay_method = validated_data['pay_method']

        # 生成订单编号
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id

        with transaction.atomic():
            # 创建保存点
            save_point = transaction.savepoint()
            try:
                # 生成订单基本信息表
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    total_count=0,
                    address=address,
                    total_amount=Decimal(0),
                    freight=Decimal(10),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                )

                # 从缓存中获取数据
                conn = get_redis_connection('cart')

                # 获取数量关系
                cart_count = conn.hgetall('cart_%s' % user.id)
                # 获取选中状态
                cart_selected = conn.smembers('cart_select_%s' % user.id)

                # 提取选中状态的数据写入到一个新字典中
                cart = {}
                for sku_id in cart_selected:
                    cart[int(sku_id)] = int(cart_count[sku_id])

                # # 获取选中状态商品数据对象
                # skus = SKU.objects.filter(id__in=cart.keys())

                for sku_id in cart.keys():
                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        sku_cout = cart[sku.id]  # 当前商品所需要的购买数量

                        old_stock = sku.stock  # 原始库存
                        old_sales = sku.sales  # 原始销量

                        # 1 判断库存
                        if sku_cout > old_stock:
                            raise serializers.ValidationError('库存不足')

                        # 2 更新库存和销量  sku表  spu表
                        new_stock = sku.stock - sku_cout
                        new_sales = sku.sales + sku_cout

                        ret = SKU.objects.filter(stock=old_stock, id=sku_id).update(sales=new_sales, stock=new_stock)
                        if ret == 0:
                            continue

                        sku.goods.sales += sku_cout
                        sku.goods.save()

                        # 更新orderinfo表
                        order.total_amount += (sku.price * sku_cout)
                        order.total_count += sku_cout

                        # 3 生成商品订单表
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_cout,
                            price=sku.price,
                        )

                        break

                # 总价累加运费
                order.total_amount += order.freight
                order.save()

            except:
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('error')
            else:
                transaction.savepoint_commit(save_point)
                # 删除缓存中的选中状态的商品数据
                conn.hdel('cart_%s' % user.id, *cart_selected)
                conn.srem('cart_select_%s' % user.id, *cart_selected)

                return order