# encoding: utf8

from .testfixtures import animal_get, animal_data

import pytest

@pytest.mark.django_db
def test_sort_by_name_no_direction(animal_get, animal_data):
    animal_data()
    response = animal_get({
            'sort': "name"
    })
    assert response.status_code == 200
    assert len(response.data) == 3
    assert  response.data[0]['name'] == 'dog'
    assert  response.data[1]['name'] == 'duck'
    assert  response.data[2]['name'] == 'tortoise'

@pytest.mark.django_db
def test_sort_by_name_direction_plus(animal_get, animal_data):
    animal_data()
    response = animal_get({
            'sort': "+name"
    })
    assert response.status_code == 200
    assert len(response.data) == 3
    assert  response.data[0]['name'] == 'dog'
    assert  response.data[1]['name'] == 'duck'
    assert  response.data[2]['name'] == 'tortoise'

@pytest.mark.django_db
def test_sort_by_name_direction_minus(animal_get, animal_data):
    animal_data()
    response = animal_get({
            'sort': "-name"
    })
    assert response.status_code == 200
    assert len(response.data) == 3
    assert  response.data[0]['name'] == 'tortoise'
    assert  response.data[1]['name'] == 'duck'
    assert  response.data[2]['name'] == 'dog'

@pytest.mark.django_db
def test_sort_by_multicolumn(animal_get, animal_data):
    animal_data()
    response = animal_get({
            'sort': "-legs, name"
    })
    assert response.status_code == 200
    assert len(response.data) == 3
    assert  response.data[0]['name'] == 'dog'
    assert  response.data[1]['name'] == 'tortoise'
    assert  response.data[2]['name'] == 'duck'

@pytest.mark.django_db
def test_sort_by_pk_direction_minus(animal_get, animal_data):
    animal_data()
    response = animal_get({
            'sort': "-id"
    })
    assert response.status_code == 200
    assert len(response.data) == 3
    assert  response.data[0]['name'] == 'duck'
    assert  response.data[1]['name'] == 'tortoise'
    assert  response.data[2]['name'] == 'dog'

@pytest.mark.django_db
def test_sort_and_filter(animal_get, animal_data):
    animal_data()
    response = animal_get({
            'filter': "name startswith 'd'",
            'sort': "-id"
    })
    assert response.status_code == 200
    assert len(response.data) == 2
    assert  response.data[0]['name'] == 'duck'
    assert  response.data[1]['name'] == 'dog'
