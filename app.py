from flask import Flask, request
import database.mongo_setup as mongo_setup
from database.people import People
from database.messages import Messages
from database.messages_to_send import MessagesToSend as Send
from iam_profile_faker.factory import V2ProfileFactory
import json
import datetime
import pytz


app = Flask(__name__)
app.secret_key = 'SeMO9wbRIu4mbm3zZlmwrNrQYNQd5jQC7wLXzmXh'

message_frequency = {'day': 1, 'week': 7, 'month': 30, 'year': 365}

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
    employee_id = json.dumps(new_emp['access_information']['hris']['values']['EmployeeID'], sort_keys=True, indent=4)
    people.slack_handle = find_slack_handle(json.dumps(new_emp['usernames']['values']))
    people.start_date = datetime.datetime.strptime(json.dumps(new_emp['created']['value']).replace('"', ''), '%Y-%m-%dT%H:%M:%S').isoformat()
    people.phone = json.dumps(new_emp['phone_numbers']['values'])
    people.manager_id = json.dumps(new_emp['access_information']['hris']['values']['WorkersManagersEmployeeID'])
    people.title = json.dumps(new_emp['access_information']['hris']['values']['businessTitle']).replace('"', '')
    people.picture = json.dumps(new_emp['picture']['value']).replace('"', '')
    people.last_updated = datetime.datetime.strptime(json.dumps(new_emp['last_modified']['value']).replace('"', ''),
                                     '%Y-%m-%dT%H:%M:%S')
    print(json.dumps(new_emp['first_name']['value'], sort_keys=True, indent=4).replace('"', ''))
    print(json.dumps(new_emp['phone_numbers']['values']))
    # print(json.dumps(new_emp, indent=4))

    people.admin_opt_out = False
    people.user_opt_out = False
    people.manager_opt_out = False

    people.save()
    print('employee id = {}'.format(employee_id))
    newly_added_user = People.objects(emp_id=employee_id)
    print('newly added user = {}'.format(newly_added_user[0].first_name))
    new_person = {}
    for p in newly_added_user:
        new_person['first_name'] = p.first_name
        new_person['last_name'] = p.last_name
        print('{} {} {} {} {} {}'.format(p.first_name, p.last_name, p.emp_id, p.start_date, p.manager_id, p.picture))
        add_messages_to_send(p)
    return 'You added {}'.format(new_person)

def find_slack_handle(socials: dict):
    """Search social media values for slack
    :param socials:
    :return:
    """
    if 'slack' in socials:
        return socials['slack']
    else:
        return 'marty331'

def add_messages_to_send(person: People):
    """
    Add each message from the messages table to the messages_to_send table when a new user is added
    :param person:
    :return:
    """
    employee_id = person.emp_id
    start_date = person.start_date
    print('start date ={}'.format(start_date))
    my_timezone = pytz.timezone(person.timezone)
    for m in Messages.objects:
        print(m)
        for x in range(0, m.number_of_sends):
            if x == 0:
                send_day = m.send_day
            else:
                print('add {}'.format(message_frequency[m.frequency]))
                send_day = send_day + message_frequency[m.frequency]

            send_date_time = start_date + datetime.timedelta(days=send_day)
            send_date_time = my_timezone.localize(send_date_time)
            send_date_time = send_date_time.replace(hour=m.send_hour, minute=0, second=0)
            print('send date time = {}'.format(send_date_time))
            to_send = Send()
            to_send.emp_id = employee_id
            to_send.message_id = m.message_id
            to_send.send_order = x
            to_send.send_dttm = send_date_time
            to_send.last_updated = datetime.datetime.now()
            to_send.save()



if __name__ == '__main__':
    print('starting app')
    main_start()
    app.debug = True
    app.run()
