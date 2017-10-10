# encoding: utf8

from rest_framework import generics, renderers

from rest_framework_filterdsl import FilterDSLBackend

from . import models
from . import serializers

class AnimalListView(generics.ListAPIView):
    queryset = models.AnimalModel.objects.all()
    serializer_class = serializers.AnimalSerializer
    renderer_classes = ( renderers.JSONRenderer,)
    filter_backends = (FilterDSLBackend,)
