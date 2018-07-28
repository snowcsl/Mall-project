import pickle

import base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response, user):
    """
    合并请求用户的购物车数据，将未登录保存在cookie里的保存到redis中
    遇到cookie与redis中出现相同的商品时以cookie数据为主，覆盖redis中的数据
    :param request: 用户的请求对象
    :param user: 当前登录的用户
    :param response: 响应对象，用于清楚购物车cookie
    :return:
    """

    cart_cookie = request.COOKIES.get('cart_cookie', None)
    # 没有cookie数据直接返回
    if not cart_cookie:
        return response
    # 解密cookie
    cart_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))

    # {sku_id1:10,sku_id2,9}
    # 拆分数据
    cart = {}
    # 选中状态数据
    cart_selected = []
    # 未选中状态
    cart_selected_none = []

    for sku_id, data_dict in cart_dict.items():

        cart[sku_id] = data_dict['count']

        if data_dict['selected']:
            cart_selected.append(sku_id)
        else:
            cart_selected_none.append(sku_id)

    # 写入缓存
    conn = get_redis_connection('cart')
    # 写入数量关系
    conn.hmset('cart_%s' % user.id, cart)
    # 写入选中状态
    if len(cart_selected):
        conn.sadd('cart_select_%s' % user.id, *cart_selected)
    if len(cart_selected_none):
        conn.srem('cart_select_%s' % user.id, *cart_selected_none)

    response.delete_cookie('cart_cookie')

    return response
