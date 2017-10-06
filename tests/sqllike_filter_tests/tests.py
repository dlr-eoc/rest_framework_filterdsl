# encoding: utf8

from django.test import TestCase
from django.core.urlresolvers import reverse

from . import models

class TestSQLLikeFilters(TestCase):
    def setUp(self):
        models.SomeModel.objects.create(title="dog")
        models.SomeModel.objects.create(title="cat")
        models.SomeModel.objects.create(title="horse")

        self.url_some_list = reverse('some-list')

    def test_get_unfiltered(self):
        response = self.client.get(self.url_some_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_get_filtered_equal(self):
        response = self.client.get(self.url_some_list, data={
                'filter': "title = 'horse'"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'horse')
