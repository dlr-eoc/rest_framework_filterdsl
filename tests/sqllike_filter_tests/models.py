# encoding: utf8

from django.db import models

class SomeModel(models.Model):
    title = models.CharField(max_length=100)

