# encoding:utf8

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^some/?$', views.SomeListView.as_view(), name="some-list"),
]
