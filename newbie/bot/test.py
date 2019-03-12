import pytest
import datetime
from .newb import app, db, session
from .newb.models import People, Messages
from .newb.routes import adjust_send_date_for_holidays_and_weekends, get_user_admin, requires_super, requires_admin, measure_date


"""
Run with:
python -m pytest -v tests/test.py
"""
class TestClass(object):

    @pytest.fixture(scope='function')
    def new_employee(self):
        print(f'new emp {datetime.datetime.now()}')
        with app.app_context():
            person = People(
                emp_id='1234',
                first_name='Bob',
                last_name='Jones',
                email='bob@jones.com',
                slack_handle='tester123',
                start_date=datetime.datetime.now(),
                last_modified=datetime.datetime.now(),
                timezone='Americas/Chicago',
                country='US',
                manager_id='boss@jones.com',
                user_opt_out=False,
                manager_opt_out=False,
                admin_opt_out=False,
                created_date=datetime.datetime.now()
            )
            db.session.add(person)
            db.session.commit()
            person = db.session.query(People).filter(People.emp_id == '1234').first()
            return person

    def test_new_employee(self, new_employee):
        """
        GIVEN a People model
        WHEN a new People is created
        THEN check the first_name, last_name, start_date, emp_id, title, country, city, picture, timezone, email,
        slack_handle, manager_id, phone, last_modified, user_opt_out, manager_opt_out and admin_opt_out
        are created correctly
        """
        assert new_employee.first_name == 'Bob'
        assert new_employee.last_name == 'Jones'
        assert not new_employee.start_date == ''
        assert new_employee.emp_id == '1234'
        assert new_employee.country == 'US'
        assert new_employee.timezone == 'Americas/Chicago'
        assert new_employee.email == 'bob@jones.com'
        assert new_employee.slack_handle == 'tester123'
        assert new_employee.manager_id == 'boss@jones.com'
        assert not new_employee.last_modified == ''
        db.session.delete(new_employee)
        db.session.commit()

    @pytest.fixture(scope='function')
    def new_message(self):
        with app.app_context():
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
                country='{ALL}',
                tags=['test', 'code', 'success'],
                team='testers',
            )
            db.session.add(message)
            db.session.commit()
            message = db.session.query(Messages).filter(Messages.type == 'test_practice').first()
            return message

    def test_new_message(self, new_message):
        assert new_message.type == 'test_practice'
        assert new_message.team == 'testers'
        assert new_message.owner == 'Mozilla'
        assert new_message.topic == 'Test Message'
        db.session.delete(new_message)
        db.session.commit()

    def test_adjust_send_date_for_holidays(self):
        """
        GIVEN a Date, Country pair
        WHEN a date is a holiday in either the US
        THEN return a date that is the next available workday
        """
        send_date_time = datetime.date(2018, 1, 1)
        country = 'US'
        send_date = adjust_send_date_for_holidays_and_weekends(send_date_time, country)
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
        send_date = adjust_send_date_for_holidays_and_weekends(send_date_time, country)
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
        send_date = adjust_send_date_for_holidays_and_weekends(send_date_time, country)
        print('send date {}'.format(send_date))
        assert send_date.weekday() <= 4
        assert send_date == datetime.date(2018, 11, 19)

    # def test_get_user_admin(self):
    #     with app.test_request_context():
    #         user_name = {'user_id':'ad|LDAP-Mozilla-mballard' }
    #         session['profile'] = user_name
    #         user = session.get('profile')['user_id']
    #         print(f'session {user}')
    #         admin = get_user_admin()
    #         print(f'admin {admin}')

    def test_measure_date(self):
        thirty = measure_date()
        current_day = datetime.datetime.today()
        delta = current_day - thirty
        assert delta.days == 30
