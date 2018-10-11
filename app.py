from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
import database.mongo_setup as mongo_setup
from database.people import People
from database.messages import Messages
from database.messages_to_send import MessagesToSend as Send
from iam_profile_faker.factory import V2ProfileFactory
import json
import datetime
import pytz
from authzero import AuthZero
import settings
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DateTimeField, IntegerField, RadioField, BooleanField



app = Flask(__name__, static_url_path='/static')
app.secret_key = 'SeMO9wbRIu4mbm3zZlmwrNrQYNQd5jQC7wLXzmXh'

message_frequency = {'day': 1, 'week': 7, 'month': 30, 'year': 365}

client_id = settings.CLIENT_ID
client_secret = settings.CLIENT_SECRET
client_uri = settings.CLIENT_URI

class AddEmployeeForm(Form):
    first_name = StringField('First Name', [validators.length(min=2, max=50)])
    last_name = StringField('Last Name', [validators.length(min=3, max=50)])
    email = StringField('Email', [validators.email(message="not a valid email")])
    city = StringField('City', [validators.length(min=2, max=50)])
    state = StringField('State', [validators.length(min=2, max=2)])
    country = StringField('Country', [validators.length(min=2, max=2)])
    timezone = StringField('Timezone')
    emp_id = IntegerField('Employee Id')
    slack_handle = StringField('Slack Handle', [validators.length(min=4, max=25)])
    start_date = StringField('Start Date')
    phone = StringField('Phone', [validators.length(min=10, max=15)])
    manager_id = IntegerField('Manager ID')
    title = StringField('Title', [validators.length(min=3, max=50)])
    picture = StringField('Picture URL')

@app.before_first_request
def main_start():
    mongo_setup.global_init()

@app.route('/')
def index():
    return render_template('home.html')

class AddMessageForm(Form):
    message_type = StringField('Message Type', [validators.required()])
    category = StringField('Category', [validators.required()])
    title = StringField('Title', [validators.required()])
    title_link = StringField('Title Link')
    send_day = IntegerField('Send Day', [validators.number_range(min=1, max=31, message='Must be valid day.')], default=1)
    send_time = IntegerField('Send Hour', [validators.number_range(min=0, max=23, message='Must be valid hour (0 - 23).')], default=9)
    frequency = StringField('Frequency')
    send_date = StringField('Send Date')
    send_once = BooleanField('Specific Date', default=False)
    text = TextAreaField('Message Value')

@app.route('/addMessage', methods=['GET', 'POST'])
def add_new_message():
    form = AddMessageForm(request.form)
    print(request.values)
    print('form errors ={}'.format(form.errors))
    if request.method == 'POST':
        if form.validate():
            message = Messages()
            message.type = form.message_type.data
            message.category = form.category.data
            message.title = form.title.data
            message.title_link = form.title_link.data
            message.send_day = form.send_day.data
            message.send_hour = form.send_time.data
            date_start = form.send_date.data.split('-')
            sdate = datetime.datetime(int(date_start[0]), int(date_start[1]), int(date_start[2]), 0, 0, 0)
            message.send_date = datetime.datetime.strftime(sdate, '%Y-%m-%dT%H:%M:%S')
            message.send_once = True if form.send_once.data == True else False
            message.frequency = form.frequency.data
            message.text = form.text.data
            message.save()
            messages = Messages.objects()
            return redirect(url_for('add_new_message'))
        else:
            print('errors = {}'.format(form.errors))
            messages = Messages.objects()
            return render_template('messages.html', messages=messages, form=form)
    messages = Messages.objects()
    return render_template('messages.html', messages=messages, form=form)



@app.route('/addEmployee', methods=['GET', 'POST'])
def add_new_employee():
    # clients = json.dumps(get_auth_zero(), sort_keys=True, indent=4)
    # print('clients = {}'.format(clients))
    print(request.method)
    form = AddEmployeeForm(request.form)
    print(request.values)
    print('form errors ={}'.format(form.errors))
    if request.method == 'POST':
        print('Post route')
        if form.validate():
            people = People()
            # factory = V2ProfileFactory()
            # new_emp = factory.create()
            # people.first_name = json.dumps(new_emp['first_name']['value'], sort_keys=True, indent=4).replace('"', '')
            # people.last_name = json.dumps(new_emp['last_name']['value'], sort_keys=True, indent=4).replace('"', '')
            # people.email = json.dumps(new_emp['primary_email']['value']).replace('"', '')
            # people.city = json.dumps(new_emp['access_information']['hris']['values']['LocationCity']).replace('"', '')
            # people.state = json.dumps(new_emp['access_information']['hris']['values']['LocationState']).replace('"', '')
            # people.country = json.dumps(new_emp['access_information']['hris']['values']['LocationCountryISO2']).replace('"', '')
            # people.timezone = json.dumps(new_emp['timezone']['value']).replace('"', '')
            # people.emp_id = json.dumps(new_emp['access_information']['hris']['values']['EmployeeID'], sort_keys=True, indent=4)
            # employee_id = json.dumps(new_emp['access_information']['hris']['values']['EmployeeID'], sort_keys=True, indent=4)
            # people.slack_handle = find_slack_handle(json.dumps(new_emp['usernames']['values']))
            # people.start_date = datetime.datetime.strptime(json.dumps(new_emp['created']['value']).replace('"', ''), '%Y-%m-%dT%H:%M:%S').isoformat()
            # people.phone = json.dumps(new_emp['phone_numbers']['values'])
            # people.manager_id = json.dumps(new_emp['access_information']['hris']['values']['WorkersManagersEmployeeID'])
            # people.title = json.dumps(new_emp['access_information']['hris']['values']['businessTitle']).replace('"', '')
            # people.picture = json.dumps(new_emp['picture']['value']).replace('"', '')
            # people.last_updated = datetime.datetime.strptime(json.dumps(new_emp['last_modified']['value']).replace('"', ''),
            #                                  '%Y-%m-%dT%H:%M:%S')
            # print(json.dumps(new_emp['first_name']['value'], sort_keys=True, indent=4).replace('"', ''))
            # print(json.dumps(new_emp['phone_numbers']['values']))
            # print('employee id = {}'.format(employee_id))
            # newly_added_user = People.objects(emp_id=employee_id)
            # print('newly added user = {}'.format(newly_added_user[0].first_name))
            # new_person = {}
            # for p in newly_added_user:
            #     new_person['first_name'] = p.first_name
            #     new_person['last_name'] = p.last_name
            #     print('{} {} {} {} {} {}'.format(p.first_name, p.last_name, p.emp_id, p.start_date, p.manager_id, p.picture))
            #     add_messages_to_send(p)
            print('user name = {}'.format(form.first_name.data))

            people.first_name = form.first_name.data
            people.last_name = form.last_name.data
            people.email = form.email.data
            people.city = form.city.data
            people.state = form.state.data
            people.country = form.country.data
            people.timezone = form.timezone.data
            people.emp_id = form.emp_id.data
            people.slack_handle = form.slack_handle.data
            date_start = form.start_date.data.split('-')
            sdate = datetime.datetime(int(date_start[0]), int(date_start[1]), int(date_start[2]), 0, 0, 0)
            people.start_date = datetime.datetime.strftime(sdate, '%Y-%m-%dT%H:%M:%S')
            people.phone = form.phone.data
            people.manager_id = form.manager_id.data
            people.title = form.title.data
            people.picture = form.picture.data
            people.last_updated = datetime.datetime.now()
            people.admin_opt_out = False
            people.user_opt_out = False
            people.manager_opt_out = False
            people.save()
            newly_added_user = People.objects(emp_id=form.emp_id.data)
            print('newly added user = {}'.format(newly_added_user[0].first_name))
            new_person = {}
            for p in newly_added_user:
                new_person['first_name'] = p.first_name
                new_person['last_name'] = p.last_name
                print('{} {} {} {} {} {}'.format(p.first_name, p.last_name, p.emp_id, p.start_date, p.manager_id, p.picture))
                add_messages_to_send(p)
            employees = People.objects()

            return redirect(url_for('add_new_employee'))
        else:
            print('errors = {}'.format(form.errors))
            return render_template('employees.html', employees=None, form=form)
    else:
        print('get route')
        employees = People.objects()

        return render_template('employees.html', employees=employees, form=form)

def get_auth_zero():
    config = {'client_id': client_id, 'client_secret': client_secret, 'uri': client_uri}
    az = AuthZero(config)
    access_token = az.get_access_token()
    return az.get_users()

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
    my_timezone = pytz.timezone(person.timezone)
    for m in Messages.objects:
        mobject = json.loads(m.to_json())
        for x in range(0, m.number_of_sends):
            if x == 0:
                send_day = m.send_day
            else:
                print('add {}'.format(message_frequency[m.frequency]))
                send_day = send_day + message_frequency[m.frequency]

            if m.send_once:
                send_date_time = m.send_date
            else:
                send_date_time = start_date + datetime.timedelta(days=send_day)
            send_date_time = my_timezone.localize(send_date_time)
            send_date_time = send_date_time.replace(hour=m.send_hour, minute=0, second=0)
            to_send = Send()
            to_send.emp_id = employee_id
            to_send.message_id = mobject['_id']['$oid']
            to_send.send_order = x
            to_send.send_dttm = send_date_time
            to_send.last_updated = datetime.datetime.now()
            to_send.save()



if __name__ == '__main__':
    print('starting app')
    main_start()
    app.debug = True
    app.run()
