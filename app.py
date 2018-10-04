from flask import Flask
import database.mongo_setup as mongo_setup
from database.people import People
from iam_profile_faker.factory import V2ProfileFactory


app = Flask(__name__)
app.secret_key = 'SeMO9wbRIu4mbm3zZlmwrNrQYNQd5jQC7wLXzmXh'

@app.before_first_request
def main_start():
    mongo_setup.global_init()


@app.route('/')
def hello_world():
    people = People()
    people.emp_id = 12349
    people.first_name = 'Maggie'
    people.last_name = 'Ballard'
    people.slack_handle = 'maggie505'
    people.admin_opt_out = False
    people.user_opt_out = False
    people.manager_opt_out = False
    people.start_date = '20180924'
    people.save()
    person = People.objects().filter(first_name='Marty').first()
    new_person = {}
    for p in People.objects:
        new_person['first_name'] = p.first_name
        new_person['last_name'] = p.last_name
    return 'You added {}'.format(new_person)


if __name__ == '__main__':
    print('starting app')
    main_start()
    factory = V2ProfileFactory()
    new_emp = factory.create()
    print('new employee = {}'.format(new_emp))
    app.debug = True
    app.run()
