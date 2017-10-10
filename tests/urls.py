from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('rest_framework_filterdsl_tests.urls')),
    url(r'^static/(?P<path>.*)$', views.serve),

]
