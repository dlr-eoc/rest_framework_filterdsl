
try:
    # django 2.0+
    from django.urls import path, include, re_path
except ImportError:
    # django 1.x
    from django.conf.urls import url as path, url as re_path
    from django.conf.urls import include

from django.contrib import admin
from django.contrib.staticfiles import views

urlpatterns = [
    path(r'^admin/', admin.site.urls),
    path(r'', include('rest_framework_filterdsl_tests.urls')),
    re_path(r'^static/(?P<path>.*)$', views.serve),

]
