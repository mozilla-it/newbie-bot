from flask import Flask, request, render_template, flash, redirect, url_for, session, make_response, Response
import database.mongo_setup as mongo_setup
from database.people import People
from database.messages import Messages
from database.messages_to_send import MessagesToSend as Send
from database.admin import Admin
from database.admin_roles import AdminRoles
from database.user_feedback import UserFeedback
from iam_profile_faker.factory import V2ProfileFactory
import json
from json_object_encoder import JSONEncoder
import datetime
import pytz
from authzero import AuthZero
import settings
import slackclient
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from mongoengine.queryset.visitor import Q
import holidays
import pymongo.errors as pymongo_errors
import mongoengine.errors as mongoengine_errors
import re

# form imports
from forms.slack_direct_message import SlackDirectMessage
from forms.add_employee_form import AddEmployeeForm
from forms.add_message_form import AddMessageForm
from forms.add_admin_role_form import AddAdminRoleForm
from forms.add_admin_form import AddAdminForm
# end form imports


import logging.config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('nhobot')
scheduler = BackgroundScheduler()

# auth
from flask_cors import CORS as cors
from flask_environ import get, collect, word_for_true
from authlib.flask.client import OAuth
from functools import wraps
import auth
import config
# endauth

current_host = 'https://nhobot.ngrok.io'

app = Flask(__name__, static_url_path='/static')
app.secret_key = settings.MONGODB_SECRET
cors(app)

client_id = settings.CLIENT_ID
client_secret = settings.CLIENT_SECRET
client_uri = settings.CLIENT_URI
client_audience = settings.CLIENT_AUDIENCE


slack_verification_token = settings.SLACK_VERIFICATION_TOKEN

slack_client = slackclient.SlackClient(settings.SLACK_BOT_TOKEN)

all_timezones = settings.all_timezones
us_holidays = holidays.US()
ca_holidays = holidays.CA()


message_frequency = {'day': 1, 'week': 7, 'month': 30, 'year': 365}

# auth
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=settings.AUTH_ID,
    client_secret=settings.AUTH_SECRET,
    api_base_url='https://' + settings.AUTH_HOST,
    access_token_url='https://' + settings.AUTH_HOST + '/oauth/token',
    authorize_url='https://' + settings.AUTH_HOST + '/authorize',
    client_kwargs={
        'scope': 'openid profile',
    },
)

app.config.update(collect(
    get('DEBUG', default=True, convert=word_for_true),
    get('HOST', default='localhost'),
    get('PORT', default=5000, convert=int),
    get('AUTH_ID', default=settings.AUTH_ID),
    get('AUTH_SECRET', default=settings.AUTH_SECRET),
    get('AUTH_HOST', default=settings.AUTH_HOST),
    get('AUTH_SCOPE', default='openid email profile'),
    get('AUTH_AUDIENCE', default=settings.AUTH_AUDIENCE),
    get('AUTH_SECRET_KEY', default=settings.AUTH_SECRET_KEY)))

AUTH_AUDIENCE = settings.AUTH_AUDIENCE
if AUTH_AUDIENCE is '':
    AUTH_AUDIENCE = 'https://' + app.config.get('HOST') + '/userinfo'

# This will be the callback URL Auth0 returns the authenticatee to.
# app.config['AUTH_URL'] = 'https://{}:{}/callback/auth'.format(app.config.get('HOST'), app.config.get('PORT'))
app.config['AUTH_URL'] = 'https://nhobot.ngrok.io/callback/auth'


oidc_config = config.OIDCConfig()
authentication = auth.OpenIDConnect(
    oidc_config
)
oidc = authentication.auth(app)
# endauth

admin_people = []

# @app.before_first_request
def main_start():
    """
    Setup processes to be ran before serving the first page.
    :return:
    """
    print('main start')
    mongo_setup.global_init()
    # slack_client.rtm_connect()
    # if scheduler.running is False:
    #     scheduler.start()
    # print('scheduler = {}'.format(scheduler.running))
    # scheduler.add_job(func=send_newhire_messages, trigger='cron', hour='*', minute='*')
    # scheduler.add_job(func=get_auth_zero, trigger='cron', hour='*', minute=31)
    # scheduler.add_job(func=updates_from_slack, trigger='cron', hour='*', minute=33)


def get_user_admin():
    try:
        userid = session.get('profile')['user_id']
        return Admin.objects(emp_id=userid).first()
    except:
        return None



def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # Redirect to Login page here
            return redirect(current_host)
        return f(*args, **kwargs)
    return decorated


def requires_super(f):
    @wraps(f)
    def decorated_super(*args, **kwargs):
        if 'profile' not in session:
            return redirect(current_host)
        userid = session.get('profile')['user_id']
        admin = Admin.objects(emp_id=userid).first()
        if admin is None or admin.super_admin is not True:
            return redirect(current_host)
        return f(*args, **kwargs)
    return decorated_super


def requires_admin(f):
    @wraps(f)
    def decorated_admin(*args, **kwargs):
        print(f'args {args}')
        print(f'kwargs {kwargs}')
        if session is None:
            return redirect(current_host)
        elif 'profile' not in session:
            return redirect(current_host)
        userid = session.get('profile')['user_id']
        print(f'requires admin {userid}')
        admin = Admin.objects(emp_id=userid).first()
        print(f'Admin {admin.emp_id}')
        print(f'Super {admin.super_admin}')
        if admin is None:
            return redirect(current_host)
        elif admin.super_admin:
            return f(*args, **kwargs)
        elif admin is None or 'Admin' not in admin.roles:
            print('not admin')
            return redirect(current_host)
        return f(*args, **kwargs)
    return decorated_admin


def requires_manager(f):
    @wraps(f)
    def decorated_manager(*args, **kwargs):
        if 'profile' not in session:
            return redirect(current_host)
        userid = session.get('profile')['user_id']
        print(f'requires admin {userid}')
        admin = Admin.objects(emp_id=userid).first()
        if admin is None:
            return redirect(current_host)
        elif admin.super_admin:
            return f(*args, **kwargs)
        elif admin is None or 'Manager' not in admin.roles:
            print('not manager')
            return redirect(current_host)
        return f(*args, **kwargs)
    return decorated_manager


@app.route('/profile')
@requires_auth
def profile():
    logger.info("User: {} authenticated proceeding to dashboard.".format(session.get('profile')['user_id']))
    user = get_user_info()
    print(json.dumps(session['jwt_payload']["https://sso.mozilla.com/claim/groups"]))
    print(json.dumps(session['jwt_payload']))
    return render_template('profile.html',
                           userinfo=session['profile'],
                           usergroups=session['jwt_payload']["https://sso.mozilla.com/claim/groups"],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4), user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    return auth0.authorize_redirect(redirect_uri=app.config.get('AUTH_URL'), audience=app.config.get('AUTH_AUDIENCE'))


@app.route('/callback/auth', methods=['GET', 'POST'])
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect(current_host)


@app.route('/logout', host='https://nhobot.ngrok.io')
def logout():
    """
    Logout and clear session
    :return:
    """
    # Clear session stored data
    session.clear()
    return redirect('https://nhobot.ngrok.io/')



@app.route('/', host='https://nhobot.ngrok.io')
def index():
    """
    Home page route
    :return: Home page
    """
    print('session {}'.format(session.get('profile')))
    user = get_user_info()
    admin = get_user_admin()
    print(f'user {user}')
    return render_template('home.html', user=user, admin=admin)


@app.route('/help')
def help_page():
    """
    Help page route
    :return: Help page
    """
    print('session {}'.format(session.get('profile')))
    user = get_user_info()
    admin = get_user_admin()
    return render_template('help.html', user=user, admin=admin)


@app.route('/addMessage', methods=['GET', 'POST'])
@requires_admin
def add_new_message():
    """
    Add new message to be sent to new hire employees
    :return:
    """
    user = get_user_info()
    admin = get_user_admin()
    form = AddMessageForm(request.form)
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
            message.send_once = True if form.send_once.data is True else False
            message.frequency = form.frequency.data
            message.text = form.text.data
            message.number_of_sends = form.number_of_sends.data
            message.country = form.country.data
            message.save()
            # messages = Messages()
            return redirect(current_host + '/addMessage')
        else:
            print('errors = {}'.format(form.errors))
            messages = Messages.objects()
            return render_template('messages.html', messages=messages, form=form, user=user, admin=admin)
    messages = Messages.objects()
    return render_template('messages.html', messages=messages, form=form, user=user, admin=admin)


@app.route('/editMessage/<string:message_id>', methods=['GET', 'POST'])
@requires_admin
def edit_message(message_id):
    """
    Update message
    :param message_id:
    :return:
    """
    print('edit message {}'.format(message_id))
    user = get_user_info()
    admin = get_user_admin()
    form = AddMessageForm(request.form)
    if request.method == 'GET':
        messages = Messages.objects(Q(id=message_id)).get()
        print(messages.type)
        form.message_type.data = messages.type
        form.category.data = messages.category
        form.title.data = messages.title
        form.title_link.data = messages.title_link
        form.send_day.data = messages.send_day
        form.send_time.data = messages.send_hour
        form.send_date.data = messages.send_date
        form.send_once.data = messages.send_once
        form.frequency.data = messages.frequency
        form.text.data = messages.text
        form.number_of_sends.data = messages.number_of_sends
        form.country.data = messages.country
        return render_template('message_edit.html', form=form, user=user, admin=admin)
    elif request.method == 'POST':
        if form.validate():
            message = Messages.objects(Q(id=message_id)).get()
            message.type = form.message_type.data
            message.category = form.category.data
            message.title = form.title.data
            message.title_link = form.title_link.data
            message.send_day = form.send_day.data
            message.send_hour = form.send_time.data
            date_start = form.send_date.data.split('-')
            sdate = datetime.datetime(int(date_start[0]), int(date_start[1]), int(date_start[2]), 0, 0, 0)
            message.send_date = datetime.datetime.strftime(sdate, '%Y-%m-%dT%H:%M:%S')
            message.send_once = True if form.send_once.data is True else False
            message.frequency = form.frequency.data
            message.text = form.text.data
            message.number_of_sends = form.number_of_sends.data
            message.country = form.country.data
            message.save()
            return redirect(current_host + '/addMessage')
        else:
            print('errors = {}'.format(form.errors))
            return redirect(current_host + '/addMessage')


@app.route('/deleteMessage/<string:message_id>')
@requires_admin
def delete_message(message_id):
    """
    Delete message from database
    :param message_id:
    :return:
    """
    Messages.objects(id=message_id).delete()
    return redirect(current_host + '/addMessage')


@app.route('/addEmployee', methods=['GET', 'POST'])
@requires_manager
def add_new_employee():
    """
    Add new employee to database
    :return:
    """
    user = get_user_info()
    admins = get_user_admin()
    print(f'add emp user {user}')
    form = AddEmployeeForm(request.form)
    if request.method == 'POST':
        if form.validate():
            people = People()
            print('user name = {}'.format(form.first_name.data))

            people.first_name = form.first_name.data
            people.last_name = form.last_name.data
            people.email = form.email.data
            people.country = form.country.data
            people.timezone = form.timezone.data
            people.emp_id = form.emp_id.data
            people.slack_handle = form.slack_handle.data
            date_start = form.start_date.data.split('-')
            sdate = datetime.datetime(int(date_start[0]), int(date_start[1]), int(date_start[2]), 0, 0, 0)
            people.start_date = datetime.datetime.strftime(sdate, '%Y-%m-%dT%H:%M:%S')
            people.manager_id = form.manager_id.data
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
                print('{} {} {} {} {}'.format(p.first_name, p.last_name, p.emp_id, p.start_date, p.manager_id))
                add_messages_to_send(p)

            return redirect(current_host + '/addEmployee')
        else:
            print('errors = {}'.format(form.errors))
            return render_template('employees.html', employees=None, form=form, selectedEmp=None,  timezones=all_timezones, user=user, admin=admins)
    else:
        admin = user['userid'].split('|')
        admin = admin[2]

        employees = []
        employee_list = People.objects()

        user_id = session.get('profile')['user_id']
        admin_data = Admin.objects(emp_id=user_id).first()
        if admin_data.super_admin:
            employees = employee_list
        else:
            for emp in employee_list:
                if re.findall(admin, emp.manager_id):
                    employees.append(emp)
        return render_template('employees.html', employees=employees, form=form, selectedEmp=None,  timezones=all_timezones, user=user, admin=admins)


@app.route('/deleteEmployee/<string:id>')
@requires_super
def delete_employee(id):
    """
    Delete employee from database
    :param id:
    :return:
    """
    People.objects(id=id).delete()
    # return redirect(url_for('add_new_employee'))
    return redirect(current_host + '/addEmployee')


@app.route('/admin', methods=['GET', 'POST'])
@requires_super
def admin_page():
    """
    Manage Admin users and roles
    :param :
    :return:
    """
    print('admin')
    form = AddAdminRoleForm(request.form)
    admin_form = AddAdminForm(request.form)
    admin_roles = AdminRoles.objects()
    admin = get_user_admin()
    peoples = People.objects()
    global admin_people
    admin_people = peoples
    # for person in peoples:
    #     admin_people.append(JSONEncoder().encode(person.to_mongo()))
    print(admin_people[10])
    role_names = [(role.role_name, role.role_description) for role in admin_roles]
    role_names = role_names[1:]
    print('role names = {}'.format(role_names))
    admin_form.roles.choices = role_names
    # TODO connect users to database after Person API is connected
    for role in admin_roles:
        print('role {}'.format(role.role_name))
    admins = Admin.objects()
    user = get_user_info()
    return render_template('admin.html', user=user, admin_roles=admin_roles, admins=admins, form=form, admin_form=admin_form, people=peoples, admin=admin)


@app.route('/adminRole', methods=['POST'])
@requires_super
def admin_role():
    """
    Add admin role to database
    :return:
    """
    form = AddAdminRoleForm(request.form)
    if request.method == 'POST':
        if form.validate():
            current_roles = AdminRoles()
            current_roles.role_name = form.role_name.data
            current_roles.role_description = form.role_description.data
            current_roles.save()
            # roles = AdminRoles.objects()
            return redirect(current_host + '/admin')
        else:
            return redirect(current_host + '/admin')
    else:
        return redirect(current_host + '/admin')


@app.route('/deleteRole/<string:role_name>')
@requires_super
def delete_role(role_name):
    """
    Delete employee from database
    :param role_name:
    :return:
    """
    AdminRoles.objects(role_name=role_name).delete()
    return redirect(current_host + '/admin')


@app.route('/adminUser', methods=['POST'])
@requires_super
def admin_user():
    """
    Add admin user to database
    :return:
    """
    admin_form = AddAdminForm(request.form)
    admin_roles = AdminRoles.objects()
    role_names = [(role.role_name, role.role_description) for role in admin_roles]
    role_names = role_names[1:]
    print(f'admin people {admin_people[11]}')
    admin_form.roles.choices = role_names
    if request.method == 'POST':
        print('admin form {}'.format(admin_form.roles.data))
        if admin_form.validate():
            admin = Admin()
            print(f'selected admin {admin_form.emp_id.data}')
            selected_admin = admin_form.emp_id.data.split(' ')
            print(f'selected admin {selected_admin}')
            admin.emp_id = selected_admin[0]
            admin.name = ' '.join(selected_admin[1:])
            admin.super_admin = admin_form.super_admin.data
            admin.roles = admin_form.roles.data
            admin.save()
            return redirect(current_host + '/admin')
        else:
            print('errors = {}'.format(admin_form.errors))
            return redirect(current_host + '/admin')
    else:
        print('errors = {}'.format(admin_form.errors))
        return redirect(current_host + '/admin')


@app.route('/deleteAdmin/<string:emp_id>')
@requires_super
def delete_admin(emp_id):
    """
    Delete employee from database
    :param emp_id:
    :return:
    """
    Admin.objects(emp_id=emp_id).delete()
    return redirect(current_host + '/admin')


def connect_slack_client():
    slack_client.rtm_connect()


def get_auth_zero():
    """
    Get Auth0 users
    :return: Auth0 user list
    """
    print('get auth zero')

    config = {'client_id': client_id, 'client_secret': client_secret, 'uri': client_uri}
    az = AuthZero(config)
    az.get_access_token()
    users = az.get_users(fields="username,user_id,name,email,identities,groups,picture,nickname,_HRData,created_at,user_metadata.groups,userinfo,app_metadata.groups,app_metadata.hris")
    for user in users:
        connection = user['identities'][0]['connection']
        if 'Mozilla-LDAP' in connection:
            user_id = user['user_id']
            current_user = People.objects(emp_id=user_id)
            if not current_user:
                name = user['name'].split()
                try:
                    manager_email = user['_HRData']['manager_email']
                except:
                    manager_email = ''
                first_name = name[0]
                last_name = name[-1]
                person = People()
                person.emp_id = user_id
                person.first_name = first_name
                person.last_name = last_name
                person.manager_id = manager_email
                country = [item for item in user['groups'] if item[:7] == 'egencia']
                if country:
                    person.country = country[0][8:].upper()
                person.email = user['email']
                person.start_date = user['created_at']
                try:
                    person.save()
                except pymongo_errors.DuplicateKeyError as error:
                    print('DuplicateKeyError {}'.format(error))
                except mongoengine_errors.NotUniqueError as error:
                    pass


def updates_from_slack():
    print('updates from slack')
    actual_one_day_ago = measure_date()
    slack_users = slack_client.api_call('users.list')['members']
    print(len(slack_users))
    people = People.objects(slack_handle=None)
    for person in people:
        slackinfo = searchemail(slack_users, 'email', person.email)
        print(slackinfo)
        if slackinfo:
            try:
                slack_handle = slackinfo['name']
                person.slack_handle = slack_handle
            except:
                slack_handle = None
            try:
                timezone = slackinfo['tz']
            except:
                timezone = 'US/Pacific'
            person.timezone = timezone
            person.save()
            print(actual_one_day_ago)
            start_date = person.start_date
            # .strptime('%Y-%m-%d')
            print('start_date {}'.format(start_date))
            print(start_date > actual_one_day_ago)
            if start_date > actual_one_day_ago:
                print('start date within 30 days {}'.format(start_date > actual_one_day_ago))
                add_messages_to_send(person)


def measure_date():
    current_day = datetime.datetime.today()
    thirty_days_ago = datetime.timedelta(days=31)
    actual_thirty_days_ago = datetime.datetime.strptime(
        datetime.datetime.strftime(current_day - thirty_days_ago, '%Y-%m-%d'), '%Y-%m-%d')
    return actual_thirty_days_ago


def find_slack_handle(socials: dict):
    """Search social media values for slack
    :param socials:
    :return:
    """
    if 'slack' in socials:
        return socials['slack']
    else:
        return 'mballard'


def add_messages_to_send(person: People):
    """
    Add each message from the messages table to the messages_to_send table when a new user is added
    :param person:
    :return:
    """
    employee_id = person.emp_id
    start_date = person.start_date
    my_timezone = pytz.timezone(person.timezone)
    my_country = person.country
    for m in Messages.objects:
        mobject = json.loads(m.to_json())
        for x in range(0, m.number_of_sends):
            if x == 0:
                send_day = m.send_day
            else:
                send_day = send_day + message_frequency[m.frequency]
            if m.send_once:
                send_date_time = m.send_date
            else:
                send_date_time = start_date + datetime.timedelta(days=send_day)
            send_date_time = my_timezone.localize(send_date_time)
            send_date_time = send_date_time.replace(hour=m.send_hour, minute=0, second=0)
            send_date_time = adjust_send_date_for_holidays_and_weekends(send_date_time, my_country)
            if m.country == 'US' and my_country == 'US':
                save_send_message(employee_id, mobject['_id']['$oid'], x, send_date_time)
            elif m.country == 'CA' and my_country == 'CA':
                save_send_message(employee_id, mobject['_id']['$oid'], x, send_date_time)
            elif m.country == 'ALL':
                save_send_message(employee_id, mobject['_id']['$oid'], x, send_date_time)
            else:
                app.logger.info('No message to be sent, user country {} and message country {}'.format(my_country, m.country))


def adjust_send_date_for_holidays_and_weekends(send_date_time, country):
    """"
    Adjust date to non-holiday or weekend
    :param send_date_time
    :param country
    :return send_date_teime
    """
    print('day num {}'.format(send_date_time.weekday()))
    weekday = send_date_time.weekday()
    if weekday > 4:
        if weekday == 6:
            send_date_time = send_date_time + datetime.timedelta(days=1)
        else:
            send_date_time = send_date_time + datetime.timedelta(days=2)
        print('weekday {}'.format(send_date_time))
        adjust_send_date_for_holidays_and_weekends(send_date_time, country)
    if country == 'US':
        print('US holiday {}'.format(send_date_time in us_holidays))
        if send_date_time in us_holidays:
            send_date_time = send_date_time + datetime.timedelta(days=1)
            adjust_send_date_for_holidays_and_weekends(send_date_time, country)
    if country == 'CA':
        print('CA holiday {}'.format(send_date_time in ca_holidays))
        if send_date_time in ca_holidays:
            send_date_time = send_date_time + datetime.timedelta(days=1)
            adjust_send_date_for_holidays_and_weekends(send_date_time, country)
    print('final send date {}'.format(send_date_time))
    return send_date_time


def save_send_message(emp_id, message_id, send_order, send_dttm):
    """
    Save to Messages to Send table
    :param emp_id:
    :param message_id:
    :param send_order:
    :param send_dttm:
    :return:
    """
    to_send = Send()
    to_send.emp_id = emp_id
    to_send.message_id = message_id
    to_send.send_order = send_order
    to_send.send_dttm = send_dttm
    to_send.last_updated = datetime.datetime.now()
    to_send.save()


def verify_slack_token(request_token):
    """
    Verity Slack token is valid
    :param request_token:
    :return: None if valid, otherwise error message
    """
    if slack_verification_token != request_token:
        print('Error: Invalid verification token')
        print('Received {}'.format(request_token))
        return make_response('Request contains invalid Slack verification token', 403)


def search(dict_list, key, value):
    for item in dict_list:
        if item[key] == value:
            return item



def searchemail(dict_list, key, value):
    for item in dict_list:
        try:
            if item['profile'][key] == value:
                return item
        except:
            pass



def slack_call_api(call_type, channel, ts, text, attachments):
    """
    Slack API call to send message and attachements
    :param call_type:
    :param channel:
    :param ts:
    :param text:
    :param attachments:
    :return:
    """
    slack_client.api_call(
        call_type,
        channel=channel,
        ts=ts,
        text=text,
        attachments=attachments
    )


@app.route('/slack/message_events', methods=['POST', 'GET'])
def message_events():
    """
    Slack message events
    :return: send Slack message events to server
    """
    print('message events')
    # form_json = json.loads(request.form.get('challenge'))
    print(json.dumps(request.get_json()))
    message_response = json.dumps(request.get_json())
    return make_response(message_response, 200)


@app.route('/slack/message_options', methods=['POST'])
def message_options():
    print('message options')
    form_json = json.loads(request.form['payload'])
    print(form_json)
    verify_slack_token(form_json['token'])
    message_attachments = []
    if form_json['name'] == 'comment':
        message_attachments = {
            'trigger_id': form_json['trigger_id'],
            'response_url': form_json['response_url'],
            'token': form_json['token'],
            'attachment_id': form_json['attachment_id'],
            'user': form_json['user'],

            'message_ts': form_json['message_ts'],
            'action_ts': form_json['action_ts'],
            'dialog': {
                'callback_id': form_json['callback_id'],
                'title': 'Comment',
                'submit_label': 'Request',
                'notify_on_cancel': True,
                'state': 'Potato',
                'elements': [
                    {
                        "label": "Additional information",
                        "name": "comment",
                        "type": "textarea",
                        "hint": "Provide additional information if needed."
                    }
                ],

            },
        }
    return Response(json.dumps(message_attachments), mimetype='application/json')

@app.route('/slack/message_actions', methods=['POST'])
def message_actions():
    """
    Slack message actions - performs action based on button message commands
    :return: Message sent to update user on action of button command
    """
    form_json = json.loads(request.form['payload'])
    callback_id = form_json['callback_id']
    if form_json['type'] == 'interactive_message':
        actions = form_json['actions'][0]['value']
        user = form_json['user']['name']
        print(f'user {user}')
        message_text = ''
        if callback_id == 'opt_out':
            if 'keep' in actions.lower():
                print('keep')
                message_text = 'We\'ll keep sending you onboarding messages!'
                People.objects(Q(slack_handle=user)).update(set__user_opt_out=False)
                slack_call_api('chat.update', form_json['channel']['id'], form_json['message_ts'], message_text,
                               '')
            elif 'stop' in actions.lower():
                print('stop')
                message_text = 'We\'ve unsubscribed you from onboarding messages.'
                People.objects(Q(slack_handle=user)).update(set__user_opt_out=True)
                slack_client.api_call(
                    'chat.update',
                    channel=form_json['channel']['id'],
                    text=message_text)
            else:
                message_text = 'Sorry, we\'re having trouble understanding you.'
                slack_call_api('chat.update', form_json['channel']['id'], form_json['message_ts'], message_text,
                               '')
        elif callback_id == 'rating':
            message_attachments = {
                    "callback_id": form_json['callback_id'],
                    "title": 'Comment',
                    "submit_label": "Submit",
                    "elements": [
                        {
                            "label": "Add comments",
                            "name": "comment",
                            "type": "textarea",
                            "hint": "We would love to hear your thoughts."
                        }
                    ],

                }
            if 'thumbsup' in actions.lower():
                print('thumbsup')
                message_attachments['state'] = 'thumbsup'
                feedback = UserFeedback()
                feedback.emp_id = form_json['user']['name']
                feedback.rating = 'thumbsup'
                feedback.comment = ''
                feedback.save()
                slack_client.api_call(
                    "dialog.open",
                    trigger_id=form_json["trigger_id"],
                    dialog=message_attachments
                )

                return make_response('', 200)
            elif 'thumbsdown' in actions.lower():
                print('thumbsdown')
                message_attachments['state'] = 'thumbsdown'
                feedback = UserFeedback()
                feedback.emp_id = form_json['user']['name']
                feedback.rating = 'thumbsdown'
                feedback.comment = ''
                feedback.save()
                feedback_val = dict(feedback.to_mongo())
                slack_client.api_call(
                    "dialog.open",
                    trigger_id=form_json["trigger_id"],
                    dialog=message_attachments
                )

                return make_response('', 200)
            else:
                message_text = 'Sorry, I didn\'t understand'
                slack_call_api('chat.update', form_json['channel']['id'], form_json['message_ts'], message_text, '')
        return make_response(message_text, 200)
    elif form_json['type'] == 'dialog_submission':
        print('dialog {}'.format(form_json))
        feedback = UserFeedback.objects(Q(emp_id=form_json['user']['name'])).all()
        created = feedback[len(feedback) - 1].created_date
        for feed in feedback:
            if feed.created_date == created:
                feed.comment = form_json['submission']['comment']
                feed.save()
        if form_json['state'] == 'thumbsdown':
            message_attachments = []
            message_attach = {
                "callback_id": "opt_out",
                "text": "Sorry to see you go",
                "replace_original": False,
                "delete_original": False,
                "fallback": "You need to upgrade your Slack client to receive this message.",
                "actions": [{
                    "name": "optout",
                    "type": "button",
                    "text": 'Opt Out',
                    "value": "stop",
                    "confirm": {
                        "title": "Are you sure?",
                        "text": "If you opt out you won\'t receive any more helpful info.",
                        "ok_text": "Yes",
                        "dismiss_text": "No"
                    }
                }]
            }
            message_attachments.insert(0, message_attach)
            print(message_attachments)
            slack_client.api_call(
                'chat.postMessage',
                channel=form_json['channel']['id'],
                text='We\'re sad to hear things aren\'t going well. \n\n '
                     'If you would like to opt-out of future messages, '
                     'click the button below.',
                attachments=message_attachments
            )
        else:
            slack_client.api_call(
                'chat.postMessage',
                channel=form_json['channel']['id'],
                text='Thanks for your feedback!',
                )
        return make_response('', 200)


@app.route('/slack/newhirehelp', methods=['POST'])
def new_hire_help():
    """
    Slack slash newhirehelp - performs action based on slash message commands
    :return: Message sent to update user on action of slash command
    """
    incoming_message = json.dumps(request.values['text']).replace('"', '')
    user = json.dumps(request.values['user_name'])
    user = user.replace('"','')
    print(f'user {user}')
    if incoming_message == 'opt-in':
        People.objects(Q(slack_handle=user)).update(set__user_opt_out=False)
        message_response = "We'll sign you back up!"
    elif incoming_message == 'help':
        message_response = 'Help will soon arrive!'
    elif incoming_message == 'opt-out':
        People.objects(Q(slack_handle=user)).update(set__user_opt_out=True)
        message_response = 'Okay, we\'ll stop sending you important tips and reminders. ' \
                           'Hope you don\'t miss any deadlines!'
    else:
        message_response = 'Sorry, I don\'t know what you want.'
    return make_response(message_response, 200)


@app.route('/slackMessage', methods=['GET', 'POST'])
@requires_admin
def send_slack_message():
    """
    Send user a test message
    :return:
    """
    user = get_user_info()
    admin = get_user_admin()
    form = SlackDirectMessage(request.form)
    slack_client.rtm_connect()
    users = slack_client.api_call('users.list')['members']
    if request.method == 'POST':
        if form.validate():
            message_text = form.message_text.data
            message_user = form.message_user.data
            user = search(users, 'name', message_user)
            print(f'user {user}')
            dm = slack_client.api_call('im.open', user=user['id'])['channel']['id']
            slack_client.rtm_send_message(dm, message_text)
            return redirect(url_for('send_slack_message'))
        else:
            print('errors = {}'.format(form.errors))
            return render_template('senddm.html', form=form, users=users, user=user, admin=admin)
    else:
        return render_template('senddm.html', form=form, users=users, user=user, admin=admin)


def send_newhire_messages():
    """
    Send new hires messages, this process is ran on a schedule
    :return:
    """
    print('send newhire messages')
    now = datetime.datetime.utcnow()
    lasthour = now - datetime.timedelta(minutes=59, seconds=59, days=7)
    print('now {}'.format(now))
    print('lasthour {}'.format(lasthour))
    send = Send.objects(Q(send_dttm__lte=now) & Q(send_dttm__gte=lasthour) & Q(send_status__exact=False))
    slack_client.rtm_connect()
    users = slack_client.api_call('users.list')['members']
    for s in send:
        print('new hire messages ={}'.format(s['send_status']))
        emp = People.objects(Q(emp_id=s['emp_id'])).get()
        if emp.user_opt_out is False and emp.manager_opt_out is False and emp.admin_opt_out is False:
            message = Messages.objects(Q(id=s['message_id'])).get().to_mongo()
            print('emp = {}'.format(emp))
            print('message = {}'.format(message))
            message_text = message['text'].split('button:')

            message_user = emp['slack_handle']
            user = search(users, 'name', message_user)
            message_attachments = []
            if user is not None:
                dm = slack_client.api_call(
                    'im.open',
                    user=user['id'],
                )['channel']['id']
                if len(message['title_link']) > 1 and len(message_text) == 1:

                    message_attach = {
                        "fallback": "You need to upgrade your Slack client to receive this message.",
                        "actions": [{
                            "type": "button",
                            "text": message['title'],
                            "url": message['title_link'],
                        }]
                    }
                    message_attachments.insert(0, message_attach)
                elif len(message_text) > 1:
                    message_actions = []
                    for x in range(1, len(message_text)):
                        action = {
                            "type": "button",
                            "text": message_text[x],
                            "name": message['title'],
                            "value": message_text[x]
                        }
                        message_actions.insert(0, action)
                    message_attach = {
                        "callback_id": message['callback_id'] if message['callback_id'] else '',
                        "fallback": "You need to upgrade your Slack client to receive this message.",
                        "actions": message_actions
                    }
                    message_attachments.insert(0, message_attach)
                    print(message_attachments)
                else:
                    app.logger.info('No message attachments.')


                slack_client.api_call(
                    'chat.postMessage',
                    channel=dm,
                    text=message_text[0],
                    attachments=message_attachments
                )
                s.update(set__send_status=True)
        else:
            s.update(set__cancel_status=True)
            print('User has opted out of notifications')

def get_user_info():
    """
    Get user session for browser
    :return:
    """
    user = None
    if (session.get('profile')):
        user = {'userid': session.get('profile')['user_id'], 'username': session.get('profile')['name'],
                'picture': session.get('profile')['picture']}
    return user


@atexit.register
def shutdown():
    """
    Register the function to be called on exit
    """
    atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    print('starting app')
    main_start()

    print('scheduler = {}'.format(scheduler.running))
    scheduler.add_job(func=send_newhire_messages, trigger='cron', hour='*', minute='*')
    scheduler.add_job(func=get_auth_zero, trigger='cron', hour='*', minute=23)
    scheduler.add_job(func=updates_from_slack, trigger='cron', hour='*', minute=58)
    if scheduler.running is False:
        scheduler.start()
    # app.debug = False
    app.use_reloader=False
    app.jinja_env.cache = {}
    app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0')
