from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.HotSKUListView.as_view()),
    url(r'^browse_histories/$', views.UserBrowsingHistoryView.as_view()),
]
