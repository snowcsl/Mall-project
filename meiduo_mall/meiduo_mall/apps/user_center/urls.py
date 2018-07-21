from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^user/$', views.UserDetailView.as_view()),
]
