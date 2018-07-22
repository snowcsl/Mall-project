from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

# 方式2
# router = DefaultRouter()
# # router.register(r'areas', views.AreasViewSet, base_name='areas')
# router.register(r'areas', views.AreasViewSet, base_name='areas')
#
# urlpatterns = []
#
# urlpatterns += router.urls


# /areas/   {'get': 'list'}  只返回顶级数据  parent=None  name=xx
# /areas/<pk>  {'get': 'retrieve'}  name=xxx

# 方式1
urlpatterns = [
    url(r'^areas/$',views.AreasView.as_view()),
    url(r'^areas/(?P<pk>\d+)/$',views.AreaView.as_view()),
]