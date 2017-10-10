# encoding: utf8

from rest_framework import serializers

from . import models

class AnimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AnimalModel
        fields = "__all__"
