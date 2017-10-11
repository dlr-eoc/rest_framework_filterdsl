# encoding: utf8

from django.utils import timezone
from datetime import timedelta

from .testfixtures import animal_get, animal_data

import pytest

@pytest.mark.django_db
def test_get_unfiltered(animal_get, animal_data):
    animal_data()
    response = animal_get({})
    assert response.status_code == 200
    assert len(response.data) == 3

@pytest.mark.django_db
def test_get_empty_filter(animal_get, animal_data):
    animal_data()
    response = animal_get({
            'filter': ''
    })
    assert response.status_code == 200
    assert len(response.data) == 3

@pytest.mark.parametrize('op', ['=', 'eq'])
@pytest.mark.django_db
def test_get_filtered_equal_string(animal_get, animal_data, op):
    animal_data()
    response = animal_get({
            'filter': "name {0} 'tortoise'".format(op)
    })
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'tortoise'

@pytest.mark.parametrize('op', ['=', 'eq'])
@pytest.mark.django_db
def test_get_filtered_equal_negative_int(animal_get, animal_data, op):
    animal_data()
    response = animal_get({
            'filter': "age {0} -3".format(op)
    })
    assert response.status_code == 200
    assert len(response.data) == 0

@pytest.mark.parametrize('op', ['=', 'eq'])
@pytest.mark.django_db
def test_get_filtered_equal_int(animal_get, animal_data, op):
    animal_data()
    response = animal_get({
            'filter': "age {0} 132".format(op)
    })
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'tortoise'

@pytest.mark.parametrize('op', ['>=', 'gte'])
@pytest.mark.django_db
def test_get_filtered_gte_int(animal_get, animal_data, op):
    animal_data()
    response = animal_get({
            'filter': "age {0} 132".format(op)
    })
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'tortoise'

@pytest.mark.parametrize('op', ['=', 'eq'])
@pytest.mark.django_db
def test_get_filtered_equal_pk(animal_get, animal_data, op):
    animal_data()
    response = animal_get({
            'filter': "id {0} 1".format(op)
    })
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'dog'

@pytest.mark.parametrize('op', ['!=', 'not eq'])
@pytest.mark.django_db
def test_get_filtered_not_equal_int(animal_get, animal_data, op):
    animal_data()
    response = animal_get({
            'filter': "age {0} 132".format(op)
    })
    #print response.data
    assert response.status_code == 200
    assert len(response.data) == 2
    animals = set([x['name'] for x in response.data])
    assert set(('dog', 'duck')) == animals

@pytest.mark.django_db
def test_get_filtered_or(animal_get, animal_data):
    animal_data()
    response = animal_get({
            'filter': "name = 'tortoise' or name = 'dog'"
    })
    assert response.status_code == 200
    assert len(response.data) == 2
    animals = set([x['name'] for x in response.data])
    assert set(('dog', 'tortoise')) == animals

@pytest.mark.parametrize('op', ['<', 'lt'])
@pytest.mark.django_db
def test_get_filtered_less_than_datettime(animal_get, animal_data, op):
    animal_data()
    response = animal_get({
            'filter': "birthday {0} '{1}'".format(
                    op,
                    (timezone.now()-timedelta(days=365*10)).isoformat()
            )
    })
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'tortoise'

@pytest.mark.django_db
def test_get_filtered_contains_string(animal_get, animal_data):
    animal_data()
    response = animal_get({
            'filter': "name contains 'rtoi'"
    })
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'tortoise'

@pytest.mark.django_db
def test_get_filtered_not_contains_string(animal_get, animal_data):
    animal_data()
    response = animal_get({
            'filter': "name not contains 'rtoi'"
    })
    assert response.status_code == 200
    assert len(response.data) == 2
    animals = set([x['name'] for x in response.data])
    assert set(('dog', 'duck')) == animals

@pytest.mark.parametrize('op', ['=', 'eq'])
@pytest.mark.django_db
def test_get_filtered_equal_boolean(animal_get, animal_data, op):
    animal_data()
    response = animal_get({
            'filter': "is_bird {0} true".format(op)
    })
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'duck'

@pytest.mark.parametrize('op', ['<', 'lt'])
@pytest.mark.django_db
def test_get_filtered_compare_fields(animal_get, animal_data, op):
    animal_data()
    response = animal_get({
            'filter': "age {0} legs".format(op)
    })
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'duck'
