# encoding: utf8

from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=100)


class AnimalModel(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    legs = models.IntegerField()
    temperature = models.DecimalField(max_digits=4, decimal_places=2)
    birthday = models.DateTimeField()
    feeding_time = models.TimeField()
    is_bird = models.BooleanField()
    favorite_food = models.CharField(max_length=100, null=True)
    owner = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name='owned_animals'
    )
    keeper = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name='kept_animals'
    )
