from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, ObtainJSONWebToken

from users.views import UserAuthorizeView
from . import views

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^users/$', views.UserView.as_view()),
    # url(r'^authorizations/$', obtain_jwt_token),  # Django REST framework JWT提供了登录签发JWT的视图，可以直接使用 完成认证过程以及写入token的过程
    #  obtain_jwt_token 结果返回只会返回token值,不显示用户名,原生的函数不能满足要求,重写
    url(r'^authorizations/$', UserAuthorizeView.as_view()),
]
