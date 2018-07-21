import re

from django.contrib.auth.backends import ModelBackend
# django原生的认证类,在类下面进行重写,因为原生中的用户名只支持字符串,为了使用户名既可以是手机号  也可以是字符串形式

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    # 只需要接收处理好的数据,只用于返回  在配置文件中可以找到此视图即可
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,  # 已经生成好的token
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(username):
    """根据账号获取用户对象"""
    try:
        # 按手机号查询
        if re.match(r'^1[3-9]\d{9}$', username):
            # 手机号
            user = User.objects.get(mobile=username)
        else:
            # 按用户名查询
            user = User.objects.get(username=username)
    except User.DoesNotExist: # 一旦捕获到异常,说明用户不存在
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """
    自定义用户名和手机号认证
    :param ModelBackend:
    :return:
    """

    def authenticate(self, request, username=None, password=None, **kwargs):  # username 接收相应框内的数据  不仅仅只带用户名
        """username可以是用户名也可以是手机号"""
        # 获取用户对象
        user = get_user_by_account(username)
        # 比对校验
        if user is not None and user.check_password(password):  # 进行密码校验
            return user
