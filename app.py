from flask import Flask, request, render_template, flash, redirect, url_for, session, make_response, jsonify, _request_ctx_stack
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
import slackclient
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from mongoengine.queryset.visitor import Q


#auth

import logging.config
logging.basicConfig(level=logging.INFO)
from flask_cors import CORS as cors

from flask_environ import get, collect, word_for_true
from authlib.flask.client import OAuth
from functools import wraps
from six.moves.urllib.parse import urlencode

import auth
import config

logger = logging.getLogger('nhobot')
#endauth

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


message_frequency = {'day': 1, 'week': 7, 'month': 30, 'year': 365}

#auth
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
#endauth


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


class AddMessageForm(Form):
    message_type = StringField('Message Type', [validators.required()])
    category = StringField('Category', [validators.required()])
    title = StringField('Title', [validators.required()])
    title_link = StringField('Title Link')
    send_day = IntegerField(
        'Send Day',
        [validators.number_range(min=1, max=31, message='Must be valid day.')],
        default=1)
    send_time = IntegerField(
        'Send Hour',
        [validators.number_range(min=0, max=23, message='Must be valid hour (0 - 23).')],
        default=9)
    frequency = StringField('Frequency')
    send_date = StringField('Send Date')
    send_once = BooleanField('Specific Date', default=False)
    text = TextAreaField('Message Value')
    number_of_sends = IntegerField(
        'Number of Sends',
        [validators.number_range(min=1, max=10, message='Must be between 1 and 10.'), validators.required()],
        default=1)
    country = StringField('Country', [validators.required()])


class SlackDirectMessage(Form):
    message_text = TextAreaField('Message Value')
    message_user = StringField('To User')


def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated


@app.route('/profile')
@requires_auth
def profile():
    logger.info("User: {} authenticated proceeding to dashboard.".format(session.get('profile')['user_id']))
    user = get_user_info()
    return render_template('profile.html',
                           userinfo=session['profile'],
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
    # Clear session stored data
    session.clear()
    return redirect('/')


@app.before_first_request
def main_start():
    mongo_setup.global_init()
    print('scheduler = {}'.format(scheduler.running))
    if scheduler.running == False:
        # scheduler.add_job(func=send_newhire_messages, trigger="interval", hours=1)
        scheduler.add_job(func=send_newhire_messages, trigger='cron', hour='*', minute=0)
        scheduler.start()


@app.route('/')
def index():
    print('session {}'.format(session.get('profile')))
    user = get_user_info()
    return render_template('home.html', user=user)

@app.route('/help')
def help():
    print('session {}'.format(session.get('profile')))
    user = get_user_info()
    return render_template('help.html', user=user)


@app.route('/addMessage', methods=['GET', 'POST'])
@requires_auth
def add_new_message():
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
            message.send_once = True if form.send_once.data == True else False
            message.frequency = form.frequency.data
            message.text = form.text.data
            message.number_of_sends = form.number_of_sends.data
            message.country = form.country.data
            message.save()
            messages = Messages()
            return redirect(url_for('add_new_message'))
        else:
            print('errors = {}'.format(form.errors))
            messages = Messages.objects()
            return render_template('messages.html', messages=messages, form=form, user=user)
    messages = Messages.objects()
    return render_template('messages.html', messages=messages, form=form, user=user)


@app.route('/deleteMessage/<string:id>')
@requires_auth
def delete_message(id):
    Messages.objects(id=id).delete()
    return redirect(url_for('add_new_message'))


@app.route('/addEmployee', methods=['GET', 'POST'])
@requires_auth
def add_new_employee():
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
            employees = People.objects()

            return redirect(url_for('add_new_employee'))
        else:
            print('errors = {}'.format(form.errors))
            return render_template('employees.html', employees=None, form=form, selectedEmp=None,  timezones=all_timezones, user=user)
    else:
        print('get route')
        employees = People.objects()

        return render_template('employees.html', employees=employees, form=form, selectedEmp=None,  timezones=all_timezones, user=user)


@app.route('/deleteEmployee/<string:id>')
@requires_auth
def delete_employee(id):
    People.objects(id=id).delete()
    return redirect(url_for('add_new_employee'))


def get_auth_zero():
    config = {'client_id': client_id, 'client_secret': client_secret, 'uri': client_uri}
    az = AuthZero(config)
    access_token = az.get_access_token()
    app.logger.info(json.dumps(access_token))
    return az.get_users(fields="username,user_id,name,email,identities,groups,picture,nickname,_HRData")


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
            if m.country == 'US' and my_country == 'US':
                save_send_message(employee_id, mobject['_id']['$oid'], x, send_date_time)
            elif m.country == 'CA' and my_country == 'CA':
                save_send_message(employee_id, mobject['_id']['$oid'], x, send_date_time)
            elif m.country == 'ALL':
                save_send_message(employee_id, mobject['_id']['$oid'], x, send_date_time)
            else:
                app.logger.info('No message to be sent, user country {} and message country {}'.format(my_country, m.country))


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
    if slack_verification_token != request_token:
        print('Error: Invalid verification token')
        print('Received {}'.format(request_token))
        return make_response('Request contains invalid Slack verification token', 403)


def search(dict_list, key, value):
    for item in dict_list:
        if item[key] == value:
            return item


def slack_call_api(call_type, channel, ts, text, attachments):
    slack_client.api_call(
        call_type,
        channel=channel,
        ts=ts,
        text=text,
        attachments=attachments
    )


@app.route('/slack/message_events', methods=['POST', 'GET'])
def message_events():
    print('message events')
    # form_json = json.loads(request.form.get('challenge'))
    print(json.dumps(request.get_json()))
    message_response = json.dumps(request.get_json())
    return make_response(message_response, 200)


@app.route('/slack/message_actions', methods=['POST'])
def message_actions():
    print('message actions route')
    form_json = json.loads(request.form['payload'])
    print('message actions = {}'.format(json.dumps(form_json, indent=4)))
    callback_id = form_json['callback_id']
    print('callback_id ={}'.format(callback_id))
    actions = form_json['actions'][0]['value']
    print('actions = {}'.format(actions))
    user = form_json['user']['name']
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
    print('newhirehelp headers = {}'.format(request.headers))
    print('newhirehelp values = {}'.format(request.values))
    incoming_message = json.dumps(request.values['text'])
    incoming_message = incoming_message.replace('"', '')
    print(incoming_message)
    if incoming_message == 'opt-in':
        message_response = "We'll sign you back up!"
    elif incoming_message == 'help':
        message_response = 'Help will soon arrive!'
    elif incoming_message == 'opt-out':
        message_response = 'Okay, we\'ll stop sending you important tips and reminders. Hope you don\'t miss any deadlines!'
    else:
        message_response = 'Sorry, I don\'t know what you want.'
    return make_response(message_response, 200)


@app.route('/slackMessage', methods=['GET', 'POST'])
@requires_auth
def send_slack_message():
    user= get_user_info()
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
    app.run(ssl_context=('cert.pem', 'key.pem'))
