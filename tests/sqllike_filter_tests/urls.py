# encoding:utf8

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^animal/?$', views.AnimalListView.as_view(), name="animal-list"),
]
