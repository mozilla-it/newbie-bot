import database.people as people
import database.mongo_setup as mongo
import pytest
import datetime

"""
Run with:
python -m pytest tests/test.py
"""


@pytest.fixture(scope='module')
def new_employee():
    mongo.global_init()
    person = people.People()
    person.first_name = 'Bob'
    person.last_name = 'Jones'
    person.start_date = datetime.datetime.now()
    person.emp_id = 123
    person.title = 'Tester'
    person.country = 'US'
    person.city = 'Houston'
    person.picture = 'https://testimage.com'
    person.timezone = 'Americas/Chicago'
    person.email = 'bob@jones.com'
    person.slack_handle = 'tester123'
    person.manager_id = 456
    person.phone = '212-555-1212'
    person.last_modified = datetime.datetime.now()
    person.save()
    return person

def test_new_employee(new_employee):
    """
    GIVEN a People model
    WHEN a new People is created
    THEN check the first_name, last_name, start_date, emp_id, title, country, city, picture, timezone, email, slack_handle, manager_id, phone, last_modified, user_opt_out, manager_opt_out and admin_opt_out are created correctly
    """
    assert new_employee.first_name == 'Bob'
    assert new_employee.last_name == 'Jones'
    assert not new_employee.start_date == ''
    assert new_employee.emp_id == 123
    assert new_employee.title == 'Tester'
    assert new_employee.country == 'US'
    assert new_employee.city == 'Houston'
    assert new_employee.picture == 'https://testimage.com'
    assert new_employee.timezone == 'Americas/Chicago'
    assert new_employee.email == 'bob@jones.com'
    assert new_employee.slack_handle == 'tester123'
    assert new_employee.manager_id == 456
    assert new_employee.phone == '212-555-1212'
    assert not new_employee.last_modified == ''