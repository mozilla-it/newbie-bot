import pytest
import datetime
import newbie
from newbie.bot.database.people import People
from newbie.bot.database import Messages



"""
Run with:
python -m pytest -v tests/test.py
"""
class TestClass(object):


    def teardown(self):
        people = People.objects(emp_id='123')
        newbie.db.session.delete(people)
        message = Messages.query.filter_by(topic='Test Message')
        newbie.db.session.delete(message)
        newbie.db.session.commit()

    @pytest.fixture(scope='module')
    def new_employee(self):
        person = People(
            first_name='Bob',
            last_name='Jones',
            start_date=datetime.datetime.now(),
            emp_id='123',
            country='US',
            city='Houston',
            picture='https://testimage.com',
            timezone='Americas/Chicago',
            email='bob@jones.com',
            slack_handle='tester123',
            manager_id='456',
            phone='212-555-1212'
        )
        newbie.db.session.add(person)
        newbie.db.session.commit()
        return person


    def test_new_employee(self, new_employee):
        """
        GIVEN a People model
        WHEN a new People is created
        THEN check the first_name, last_name, start_date, emp_id, title, country, city, picture, timezone, email, slack_handle, manager_id, phone, last_modified, user_opt_out, manager_opt_out and admin_opt_out are created correctly
        """
        assert new_employee.first_name == 'Bob'
        assert new_employee.last_name == 'Jones'
        assert not new_employee.start_date == ''
        assert new_employee.emp_id == '123'
        assert new_employee.country == 'US'
        assert new_employee.city == 'Houston'
        assert new_employee.picture == 'https://testimage.com'
        assert new_employee.timezone == 'Americas/Chicago'
        assert new_employee.email == 'bob@jones.com'
        assert new_employee.slack_handle == 'tester123'
        assert new_employee.manager_id == '456'
        assert new_employee.phone == '212-555-1212'
        assert not new_employee.last_modified == ''

    @pytest.fixture(scope='module')
    def new_message(self):
        message = Messages(
            type='test_practice',
            topic='Test Message',
            title_link=[{"name": "test", "url": "https://www.example.com"}],
            send_day=7,
            send_hour=9,
            repeatable=False,
            text='Hi, I\'m a test message and you\'re not.',
            send_date=datetime.datetime.now(),
            send_once=True,
            country='ALL',
            tags=['test', 'code', 'success'],
            team='testers',
        )
        newbie.db.session.add(message)
        newbie.db.session.commit()
        return message

    def test_new_message(self, new_message):
        assert new_message.type == 'test_practice'
        assert new_message.team == 'testers'
        assert new_message.owner == 'Mozilla'
        assert new_message.topic == 'Test Message'


    def test_adjust_send_date_for_holidays(self):
        """
        GIVEN a Date, Country pair
        WHEN a date is a holiday in either the US
        THEN return a date that is the next available workday
        """
        send_date_time = datetime.date(2018, 1, 1)
        country = 'US'
        send_date = newbie.adjust_send_date_for_holidays_and_weekends(send_date_time, country)
        assert not send_date == datetime.date(2018, 1, 1)
        assert send_date == datetime.date(2018, 1, 2)
        print('send date {}'.format(send_date))



    def test_saturday_date(self):
        """
           GIVEN a Date, Country pair
           WHEN a date is a saturday in either the US
           THEN return a date that is the next available workday
           """
        send_date_time = datetime.date(2018, 11, 24)
        country = 'US'
        send_date = newbie.adjust_send_date_for_holidays_and_weekends(send_date_time, country)
        print('send date {}'.format(send_date))
        assert send_date.weekday() <= 4
        assert send_date == datetime.date(2018, 11, 26)


    def test_sunday_date(self):
        """
           GIVEN a Date, Country pair
           WHEN a date is a sunday in either the US
           THEN return a date that is the next available workday
           """
        send_date_time = datetime.date(2018, 11, 18)
        country = 'US'
        send_date = newbie.adjust_send_date_for_holidays_and_weekends(send_date_time, country)
        print('send date {}'.format(send_date))
        assert send_date.weekday() <= 4
        assert send_date == datetime.date(2018, 11, 19)
