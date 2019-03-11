# encoding: utf8

import pytest

try:
    # django 2.0+
    from django.urls import reverse_lazy
except ImportError:
    # django 1.x
    from django.core.urlresolvers import reverse_lazy
from django.utils import timezone

from datetime import timedelta, time

from . import models

@pytest.fixture()
def animal_get(client):
    def get(params):
        return client.get(reverse_lazy('animal-list'), data=params)
    return get

@pytest.fixture()
def animal_data(db):
    def create():
        a_person = models.Person.objects.create(
                name="A",
        )
        b_person = models.Person.objects.create(
                name="B",
        )
        models.AnimalModel.objects.create(
                name="dog",
                age=5,
                legs=4,
                birthday=timezone.now() - timedelta(days=365*5),
                is_bird=False,
                feeding_time=time(hour=10),
                owner=a_person,
                keeper=a_person,
        )
        models.AnimalModel.objects.create(
                name="tortoise",
                age=132,
                legs=4,
                birthday=timezone.now() - timedelta(days=365*132),
                is_bird=False,
                favorite_food='tomato',
                feeding_time=time(hour=15),
                owner=a_person,
                keeper=a_person,
        )
        models.AnimalModel.objects.create(
                name="duck",
                age=1,
                legs=2,
                birthday=timezone.now() - timedelta(days=365*3),
                is_bird=True,
                feeding_time=time(hour=20),
                owner=b_person,
                keeper=b_person,
        )
    return create
