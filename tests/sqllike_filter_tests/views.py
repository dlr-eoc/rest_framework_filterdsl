# encoding: utf8

from rest_framework import generics, renderers

from rf_sqllike_filter.filters import SQLLikeFilterBackend

from . import models
from . import serializers

class SomeListView(generics.ListAPIView):
    queryset = models.SomeModel.objects.all()
    serializer_class = serializers.SomeSerializer
    renderer_classes = ( renderers.JSONRenderer,)
    filter_backends = (SQLLikeFilterBackend,)
