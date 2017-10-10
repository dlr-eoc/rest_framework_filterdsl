# encoding: utf8

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone

from unittest import skip
from datetime import timedelta

from . import models


class BaseTestCase(TestCase):

    def setUp(self):
        models.AnimalModel.objects.create(
                name="dog",
                age=5,
                legs=4,
                birthday=timezone.now() - timedelta(days=365*5),
                is_bird=False
        )
        models.AnimalModel.objects.create(
                name="tortoise",
                age=132,
                legs=4,
                birthday=timezone.now() - timedelta(days=365*132),
                is_bird=False
        )
        models.AnimalModel.objects.create(
                name="duck",
                age=3,
                legs=2,
                birthday=timezone.now() - timedelta(days=365*3),
                is_bird=True
        )

        self.url_animal_list = reverse('animal-list')


class TestFilters(BaseTestCase):

    def test_get_unfiltered(self):
        response = self.client.get(self.url_animal_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_get_empty_filter(self):
        response = self.client.get(self.url_animal_list, data={
                'filter': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_get_filtered_equal_string(self):
        response = self.client.get(self.url_animal_list, data={
                'filter': "name = 'tortoise'"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'tortoise')

    def test_get_filtered_equal_negative_int(self):
        response = self.client.get(self.url_animal_list, data={
                'filter': "age = -3"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_get_filtered_equal_int(self):
        response = self.client.get(self.url_animal_list, data={
                'filter': "age = 132"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'tortoise')

    def test_get_filtered_not_equal_int(self):
        response = self.client.get(self.url_animal_list, data={
                'filter': "age != 132"
        })
        #print response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        animals = set([x['name'] for x in response.data])
        self.assertEqual(set(('dog', 'duck')), animals)

    def test_get_filtered_or(self):
        response = self.client.get(self.url_animal_list, data={
                'filter': "name = 'tortoise' or name = 'dog'"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        animals = set([x['name'] for x in response.data])
        self.assertEqual(set(('dog', 'tortoise')), animals)

    def test_get_filtered_less_than_datettime(self):
        response = self.client.get(self.url_animal_list, data={
                'filter': "birthday < '{0}'".format((timezone.now()-timedelta(days=365*10)).isoformat())
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'tortoise')

    def test_get_filtered_contains_string(self):
        response = self.client.get(self.url_animal_list, data={
                'filter': "name contains 'rtoi'"
        })
        #print response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'tortoise')

    def test_get_filtered_equal_boolean(self):
        response = self.client.get(self.url_animal_list, data={
                'filter': "is_bird = true"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'duck')


class TestSorting(BaseTestCase):

    def test_sort_by_name_no_direction(self):
        response = self.client.get(self.url_animal_list, data={
                'sort': "name"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['name'], 'dog')
        self.assertEqual(response.data[1]['name'], 'duck')
        self.assertEqual(response.data[2]['name'], 'tortoise')

    def test_sort_by_name_direction_plus(self):
        response = self.client.get(self.url_animal_list, data={
                'sort': "+name"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['name'], 'dog')
        self.assertEqual(response.data[1]['name'], 'duck')
        self.assertEqual(response.data[2]['name'], 'tortoise')

    def test_sort_by_name_direction_minus(self):
        response = self.client.get(self.url_animal_list, data={
                'sort': "-name"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['name'], 'tortoise')
        self.assertEqual(response.data[1]['name'], 'duck')
        self.assertEqual(response.data[2]['name'], 'dog')

    def test_sort_by_multicolumn(self):
        response = self.client.get(self.url_animal_list, data={
                'sort': "-legs, name"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['name'], 'dog')
        self.assertEqual(response.data[1]['name'], 'tortoise')
        self.assertEqual(response.data[2]['name'], 'duck')
