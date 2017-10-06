# encoding: utf8

from rest_framework import serializers

from . import models

class SomeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SomeModel
        fields = "__all__"
