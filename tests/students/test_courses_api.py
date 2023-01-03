import random
import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Course, Student


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def course(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return course


@pytest.fixture
def student_factory():
    def student(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return student


@pytest.mark.django_db
def test_get_course(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.get('/api/v1/courses/1/')
    data = response.json()
    assert response.status_code == 200
    assert course[0].name == data['name']


@pytest.mark.django_db
def test_get_course_list(client, course_factory):
    courses = course_factory(_quantity=20)
    response = client.get('/api/v1/courses/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(courses)
    for i, course in enumerate(data):
        assert courses[i].name == course['name']


@pytest.mark.django_db
def test_filter_for_id(client, course_factory):
    courses = course_factory(_quantity=20)
    number = random.choice(range(20))
    course = courses[number]
    response = client.get('/api/v1/courses/', {'id': course.id})
    assert response.status_code == 200
    data = response.json()
    assert course.id == data[0]['id']


@pytest.mark.django_db
def test_filter_for_name(client, course_factory):
    courses = course_factory(_quantity=20)
    number = random.choice(range(20))
    course = courses[number]
    response = client.get('/api/v1/courses/', {'name': course.name})
    assert response.status_code == 200
    data = response.json()
    assert course.name == data[0]['name']


@pytest.mark.django_db
def test_create_course(client):
    count = Course.objects.count()
    data = {'name': 'best_course', 'students': []}
    response = client.post('/api/v1/courses/', data, format='json')
    assert response.status_code == 201
    assert Course.objects.count() == count + 1


@pytest.mark.django_db
def test_update_course(client, course_factory):
    courses = course_factory(_quantity=20)
    course = courses[random.choice(range(20))]
    new_course = {'name': 'best_course'}

    url = f'/api/v1/courses/{course.id}/'
    response = client.put(url, new_course)

    assert response.status_code == 200
    data = response.json()
    assert new_course['name'] == data['name']


@pytest.mark.django_db
def test_delete_course(client, course_factory):
    courses = course_factory(_quantity=20)
    course = courses[random.choice(range(20))]

    response = client.delete(f'/api/v1/courses/{course.id}/')
    assert response.status_code == 204

    response = client.get(f'/api/v1/courses/')
    data = response.json()
    ids = [course['id'] for course in data]
    assert course.id not in ids


@pytest.mark.django_db
def test_number_of_students(client, student_factory, settings):
    students = student_factory(_quantity=50)
    course_data = {'name': 'best_course', 'students': [i for i in range(1, 15)]}
    response = client.post('/api/v1/courses/', course_data, format='json')
    assert response.status_code == 201
    data = response.json()
    assert len(data['students']) <= settings.MAX_STUDENTS_PER_COURSE
