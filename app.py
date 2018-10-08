from flask import Flask, request
import database.mongo_setup as mongo_setup
from database.people import People
from database.messages import Messages
from iam_profile_faker.factory import V2ProfileFactory
import json
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'SeMO9wbRIu4mbm3zZlmwrNrQYNQd5jQC7wLXzmXh'

@app.before_first_request
def main_start():
    mongo_setup.global_init()


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/addMessage', methods=['GET', 'POST'])
def add_new_message():
    print(request.values)
    message_id = request.values['message_id']
    message_type = request.values['type']
    category = request.values['category']
    title = request.values['title']
    title_link = request.values['title_link']
    send_day = request.values['send_day']
    send_time = request.values['send_time']
    frequency = request.values['frequency']
    text = request.values['text']
    print(message_id)
    print(message_type)
    message = Messages();
    message.message_id = message_id
    message.type = message_type
    message.category = category
    message.title = title
    message.title_link = title_link
    message.send_day = send_day
    message.send_hour = send_time
    message.frequency = frequency
    message.text = text
    message.save()
    return 'added {} {}'.format(message_id, title)

@app.route('/addEmployee', methods=['GET', 'POST'])
def add_new_employee():
    factory = V2ProfileFactory()
    new_emp = factory.create()
    people = People()
    people.first_name = json.dumps(new_emp['first_name']['value'], sort_keys=True, indent=4).replace('"', '')
    people.last_name = json.dumps(new_emp['last_name']['value'], sort_keys=True, indent=4).replace('"', '')
    people.email = json.dumps(new_emp['primary_email']['value']).replace('"', '')
    people.city = json.dumps(new_emp['access_information']['hris']['values']['LocationCity']).replace('"', '')
    people.state = json.dumps(new_emp['access_information']['hris']['values']['LocationState']).replace('"', '')
    people.country = json.dumps(new_emp['access_information']['hris']['values']['LocationCountryISO2']).replace('"', '')
    people.timezone = json.dumps(new_emp['timezone']['value']).replace('"', '')
    people.emp_id = json.dumps(new_emp['access_information']['hris']['values']['EmployeeID'], sort_keys=True, indent=4)
    people.slack_handle = json.dumps(new_emp['usernames']['values'])
    people.start_date = datetime.strptime(json.dumps(new_emp['created']['value']).replace('"', ''), '%Y-%m-%dT%H:%M:%S')
    people.phone = json.dumps(new_emp['phone_numbers']['values'])
    people.manager_id = json.dumps(new_emp['access_information']['hris']['values']['WorkersManagersEmployeeID'])
    people.title = json.dumps(new_emp['access_information']['hris']['values']['businessTitle']).replace('"', '')
    people.picture = json.dumps(new_emp['picture']['value']).replace('"', '')
    people.last_updated = datetime.strptime(json.dumps(new_emp['last_modified']['value']).replace('"', ''),
                                     '%Y-%m-%dT%H:%M:%S')
    print(json.dumps(new_emp['first_name']['value'], sort_keys=True, indent=4).replace('"', ''))
    print(json.dumps(new_emp['phone_numbers']['values']))
    print(json.dumps(new_emp, indent=4))

    people.admin_opt_out = False
    people.user_opt_out = False
    people.manager_opt_out = False

    people.save()
    new_person = {}
    for p in People.objects:
        new_person['first_name'] = p.first_name
        new_person['last_name'] = p.last_name
    return 'You added {}'.format(new_person)

if __name__ == '__main__':
    print('starting app')
    main_start()
    app.debug = True
    app.run()
