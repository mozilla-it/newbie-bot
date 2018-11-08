from flask import Flask, request, render_template, flash, redirect, url_for, session, make_response, jsonify, _request_ctx_stack
import database.mongo_setup as mongo_setup
from database.people import People
from database.messages import Messages
from database.messages_to_send import MessagesToSend as Send
from database.admin import Admin
from database.admin_roles import AdminRoles
from iam_profile_faker.factory import V2ProfileFactory
import json
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

# auth
from flask_cors import CORS as cors
from flask_environ import get, collect, word_for_true
from authlib.flask.client import OAuth
from functools import wraps
import auth
import config
# endauth

# job_defaults = {
#     'coalesce': False,
#     'max_instances': 3
# }
# scheduler = BackgroundScheduler(job_defaults=job_defaults)
scheduler = BackgroundScheduler()

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
app.config['AUTH_URL'] = 'https://{}:{}/callback/auth'.format(app.config.get('HOST'), app.config.get('PORT'))


oidc_config = config.OIDCConfig()
authentication = auth.OpenIDConnect(
    oidc_config
)
oidc = authentication.auth(app)
# endauth



@app.before_first_request
def main_start():
    """
    Setup processes to be ran before serving the first page.
    :return:
    """
    mongo_setup.global_init()
    # slack_client.rtm_connect()
    print('scheduler = {}'.format(scheduler.running))
    if scheduler.running is not True:
        # scheduler.add_job(func=send_newhire_messages, trigger='cron', hour='*', minute='*')
        scheduler.add_job(func=get_auth_zero, trigger='cron', hour='*', minute='*/2')
        # scheduler.add_job(func=updates_from_slack, trigger='cron', hour='*', minute='*/3')
        scheduler.add_job(func=updates_from_slack, trigger='cron', hour='*', minute='*')
        scheduler.start()


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # Redirect to Login page here
            return redirect('/')
        return f(*args, **kwargs)
    return decorated


def requires_super(f):
    @wraps(f)
    def decorated_super(*args, **kwargs):
        if 'profile' not in session:
            return redirect('/')
        userid = session.get('profile')['user_id']
        admin = Admin.objects(emp_id=userid).first()
        if admin is None or admin.super_admin is not True:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_super


def requires_admin(f):
    @wraps(f)
    def decorated_admin(*args, **kwargs):
        if 'profile' not in session:
            return redirect('/')
        userid = session.get('profile')['user_id']
        admin = Admin.objects(emp_id=userid).first()
        if admin.super_admin:
            return f(*args, **kwargs)
        elif admin is None or 'Admin' not in admin.roles:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_admin


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
    return redirect('/')


@app.route('/logout')
def logout():
    """
    Logout and clear session
    :return:
    """
    # Clear session stored data
    session.clear()
    return redirect('/')



@app.route('/')
def index():
    """
    Home page route
    :return: Home page
    """
    print('session {}'.format(session.get('profile')))
    user = get_user_info()
    return render_template('home.html', user=user)


@app.route('/help')
def help_page():
    """
    Help page route
    :return: Help page
    """
    print('session {}'.format(session.get('profile')))
    user = get_user_info()
    return render_template('help.html', user=user)


@app.route('/addMessage', methods=['GET', 'POST'])
@requires_admin
def add_new_message():
    """
    Add new message to be sent to new hire employees
    :return:
    """
    user = get_user_info()
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
            return redirect(url_for('add_new_message'))
        else:
            print('errors = {}'.format(form.errors))
            messages = Messages.objects()
            return render_template('messages.html', messages=messages, form=form, user=user)
    messages = Messages.objects()
    return render_template('messages.html', messages=messages, form=form, user=user)


@app.route('/editMessage/<string:id>')
@requires_admin
def edit_message(message_id):
    """
    Update message
    :param message_id:
    :return:
    """
    print('edit message {}'.format(message_id))
    return redirect(url_for('add_new_message'))


@app.route('/deleteMessage/<string:id>')
@requires_admin
def delete_message(message_id):
    """
    Delete message from database
    :param message_id:
    :return:
    """
    Messages.objects(id=message_id).delete()
    return redirect(url_for('add_new_message'))


@app.route('/addEmployee', methods=['GET', 'POST'])
@requires_auth
def add_new_employee():
    """
    Add new employee to database
    :return:
    """
    user = get_user_info()
    form = AddEmployeeForm(request.form)
    if request.method == 'POST':
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

            return redirect(url_for('add_new_employee'))
        else:
            print('errors = {}'.format(form.errors))
            return render_template('employees.html', employees=None, form=form, selectedEmp=None,  timezones=all_timezones, user=user)
    else:
        print('get route')
        employees = People.objects()

        return render_template('employees.html', employees=employees, form=form, selectedEmp=None,  timezones=all_timezones, user=user)


@app.route('/deleteEmployee/<string:id>')
@requires_super
def delete_employee(id):
    """
    Delete employee from database
    :param id:
    :return:
    """
    People.objects(id=id).delete()
    return redirect(url_for('add_new_employee'))


@app.route('/admin', methods=['GET', 'POST'])
@requires_super
def admin_page():
    """
    Manage Admin users and roles
    :param :
    :return:
    """
    form = AddAdminRoleForm(request.form)
    admin_form = AddAdminForm(request.form)
    admin_roles = AdminRoles.objects()
    role_names = [(role.role_name, role.role_description) for role in admin_roles]
    role_names = role_names[1:]
    print('role names = {}'.format(role_names))
    admin_form.roles.choices = role_names
    # TODO connect users to database after Person API is connected
    for role in admin_roles:
        print('role {}'.format(role.role_name))
    admins = Admin.objects()
    user = get_user_info()
    return render_template('admin.html', user=user, admin_roles=admin_roles, admins=admins, form=form, admin_form=admin_form)


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
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('admin_page'))
    else:
        return redirect(url_for('admin_page'))


@app.route('/deleteRole/<string:role_name>')
@requires_super
def delete_role(role_name):
    """
    Delete employee from database
    :param role_name:
    :return:
    """
    AdminRoles.objects(role_name=role_name).delete()
    return redirect(url_for('admin_page'))


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
    print('role names = {}'.format(role_names))
    admin_form.roles.choices = role_names
    if request.method == 'POST':
        print('admin form {}'.format(admin_form.roles.data))
        if admin_form.validate():
            admin = Admin()
            admin.emp_id = admin_form.emp_id.data
            admin.name = admin_form.name.data
            admin.super_admin = admin_form.super_admin.data
            admin.roles = admin_form.roles.data
            admin.save()
            return redirect(url_for('admin_page'))
        else:
            print('errors = {}'.format(admin_form.errors))
            return redirect(url_for('admin_page'))
    else:
        print('errors = {}'.format(admin_form.errors))
        return redirect(url_for('admin_page'))


@app.route('/deleteAdmin/<string:emp_id>')
@requires_super
def delete_admin(emp_id):
    """
    Delete employee from database
    :param emp_id:
    :return:
    """
    Admin.objects(emp_id=emp_id).delete()
    return redirect(url_for('admin_page'))


def connect_slack_client():
    slack_client.rtm_connect()


def get_auth_zero():
    """
    Get Auth0 users
    :return: Auth0 user list
    """
    print('get auth zero')
    actual_one_day_ago = measure_date()
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
                    print('NotUniqueError {}'.format(error))
                # print(actual_one_day_ago)
                # print(person.start_date[:10])
                # start_date = datetime.datetime.strptime(person.start_date[:10], '%Y-%m-%d')
                # print(start_date)
                # if start_date > actual_one_day_ago:
                #     print('start date within 30 days {}'.format(start_date > actual_one_day_ago))


def updates_from_slack():
    print('updates from slack')
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
            add_messages_to_send(person)


def measure_date():
    current_day = datetime.datetime.today()
    thirty_days_ago = datetime.timedelta(days=30)
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
        print('messages to send = {}'.format(mobject))
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
    # form_json = json.loads(request.form.get('challenge'))
    print(json.dumps(request.get_json()))
    message_response = json.dumps(request.get_json())
    return make_response(message_response, 200)


@app.route('/slack/message_actions', methods=['POST'])
def message_actions():
    """
    Slack message actions - performs action based on button message commands
    :return: Message sent to update user on action of button command
    """
    form_json = json.loads(request.form['payload'])
    callback_id = form_json['callback_id']
    actions = form_json['actions'][0]['value']
    user = form_json['user']['name']
    message_text = ''
    if callback_id == 'opt_out':
        if 'keep' in actions.lower():
            message_text = 'We\'ll keep sending you onboarding messages!'
            People.objects(Q(slack_handle=user)).update(set__user_opt_out=False)
        elif 'stop' in actions.lower():
            message_text = 'We\'ve unsubscribed you from onboarding messages.'
            People.objects(Q(slack_handle=user)).update(set__user_opt_out=True)
        else:
            message_text = 'Sorry, we\'re having trouble understanding you.'
        slack_call_api('chat.update', form_json['channel']['id'], form_json['message_ts'], message_text, '')
    return make_response(message_text, 200)


@app.route('/slack/newhirehelp', methods=['POST'])
def new_hire_help():
    """
    Slack slash newhirehelp - performs action based on slash message commands
    :return: Message sent to update user on action of slash command
    """
    incoming_message = json.dumps(request.values['text']).replace('"', '')
    user = json.dumps(request.values['user_name'])
    if incoming_message == 'opt-in':
        message_response = "We'll sign you back up!"
        People.objects(Q(slack_handle=user)).update(set__user_opt_out=False)
    elif incoming_message == 'help':
        message_response = 'Help will soon arrive!'
    elif incoming_message == 'opt-out':
        message_response = 'Okay, we\'ll stop sending you important tips and reminders. ' \
                           'Hope you don\'t miss any deadlines!'
        People.objects(Q(slack_handle=user)).update(set__user_opt_out=True)
    else:
        message_response = 'Sorry, I don\'t know what you want.'
    return make_response(message_response, 200)


@app.route('/slackMessage', methods=['GET', 'POST'])
@requires_auth
def send_slack_message():
    """
    Send user a test message
    :return:
    """
    user = get_user_info()
    form = SlackDirectMessage(request.form)
    slack_client.rtm_connect()
    users = slack_client.api_call('users.list')['members']
    if request.method == 'POST':
        if form.validate():
            message_text = form.message_text.data
            message_user = form.message_user.data
            user = search(users, 'name', message_user)
            dm = slack_client.api_call('im.open', user=user['id'])['channel']['id']
            slack_client.rtm_send_message(dm, message_text)
            return redirect(url_for('send_slack_message'))
        else:
            print('errors = {}'.format(form.errors))
            return render_template('senddm.html', form=form, users=users, user=user)
    else:
        return render_template('senddm.html', form=form, users=users, user=user)


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
            print('link = {}'.format(len(message['title_link'])))
            help_attach = {
                "fallback": "You need to upgrade your Slack client to receive this message.",
                "actions": [{
                    "type": "button",
                    "text": 'Help',
                    "url": 'https://mozilla.com',
                }]
            }
            message_attachments = [help_attach]

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
            else:
                app.logger.info('No message attachments.')

            dm = slack_client.api_call(
                'im.open',
                user=user['id'],
            )['channel']['id']
            slack_client.api_call(
                'chat.postMessage',
                channel=dm,
                text=message_text[0],
                attachments=message_attachments
            )
            # else:
            #     dm = slack_client.api_call(
            #         'im.open',
            #         user=user['id'],
            #         attachments=[message_attach],
            #         text=message_text
            #     )['channel']['id']
            #     slack_client.rtm_send_message(dm, message_text)
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
    app.debug = True
    app.use_reloader=False
    app.run(ssl_context=('cert.pem', 'key.pem'))
