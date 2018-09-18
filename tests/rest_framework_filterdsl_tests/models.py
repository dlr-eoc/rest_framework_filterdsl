# encoding: utf8

from django.db import models

class AnimalModel(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    legs = models.IntegerField()
    birthday = models.DateTimeField()
    is_bird = models.BooleanField()
    favorite_food = models.CharField(max_length=100, null=True)
