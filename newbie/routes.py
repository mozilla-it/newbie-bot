from newbie.database.people import People
from newbie.database.messages import Messages
from newbie.database.messages_to_send import MessagesToSend as Send
from newbie.database.admin import Admin
from newbie.database.admin_roles import AdminRoles
from newbie.database.user_feedback import UserFeedback
from newbie.database.auth_groups import AuthGroups
from newbie import db
from sqlalchemy.exc import IntegrityError

# form imports
from newbie.forms.slack_direct_message import SlackDirectMessage
from newbie.forms.add_employee_form import AddEmployeeForm
from newbie.forms.add_message_form import AddMessageForm
from newbie.forms.add_admin_role_form import AddAdminRoleForm
from newbie.forms.add_admin_form import AddAdminForm
from newbie.forms.add_admin_request import AddAdminRequest
from newbie.forms.pending_requests_form import PendingRequestsForm
# end form imports

from newbie import app, session, redirect, current_host, wraps, slack_client, \
    message_frequency, client_id, client_secret, client_uri, us_holidays, ca_holidays, \
    make_response, slack_verification_token, render_template, auth0, logger, request, \
    Response, url_for, all_timezones
import json
import datetime
import pytz

import re
from authzero import AuthZero

def get_user_admin():
    try:
        userid = session.get('profile')['user_id']
        print(f'userid {userid}')
        return Admin.query.filter_by(emp_id=userid).first()
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
        print(f'super userid {userid}')
        admin = Admin.query.filter_by(emp_id=userid).first()
        print(f'super admin {admin}')
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
        admin = Admin.query.filter_by(emp_id=userid).first()
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
        print(f'requires manager {userid}')
        admin = Admin.query.filter_by(emp_id=userid).first()
        if admin is None:
            return redirect(current_host)
        elif admin.super_admin:
            return f(*args, **kwargs)
        elif admin is None or 'Manager' not in admin.roles:
            print('not manager')
            return redirect(current_host)
        return f(*args, **kwargs)
    return decorated_manager


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
    users = az.get_users(fields="username,user_id,name,email,identities,"
                                "groups,picture,nickname,_HRData,created_at,"
                                "user_metadata.groups,userinfo,app_metadata.groups,app_metadata.hris")
    for user in users:
        if 'groups' in user:
            groups = user["groups"]
            for group in groups:
                auth_group = AuthGroups.query.filter_by(groups=group).first()
                if not auth_group:
                    auth = AuthGroups(groups=group)
                    db.session.add(auth)
                    db.session.commit()
                if 'manager' in group:
                    admin = Admin.query.filter_by(emp_id=user['user_id']).first()
                    if not admin:
                        new_admin = Admin(emp_id=user['user_id'], name=user['name'], roles=['Manager'])
                        db.session.add(new_admin)
                        db.session.commit()
        connection = user['identities'][0]['connection']
        if 'Mozilla-LDAP' in connection:
            user_id = user['user_id']
            current_user = People.query.filter_by(emp_id=user_id).first()
            if not current_user:
                name = user['name'].split()
                try:
                    manager_email = user['_HRData']['manager_email']
                except:
                    manager_email = ''
                first_name = name[0]
                last_name = name[-1]
                country = [item for item in user['groups'] if item[:7] == 'egencia']
                person_country = ''
                if country:
                    person_country = country[0][8:].upper()
                dnow = datetime.datetime.utcnow()
                person = People(emp_id=user_id, first_name=first_name, last_name=last_name,
                                   email=user['email'], slack_handle='', start_date=user['created_at'],
                                   last_modified=dnow, timezone='', country=person_country,
                                   manager_id=manager_email, user_opt_out=False, manager_opt_out=False,
                                   admin_opt_out=False, created_date=dnow)
                db.session.add(person)
                try:
                    db.session.commit()
                except IntegrityError as error:
                    print('DuplicateKeyError {}'.format(error))
                    db.session.rollback()


def updates_from_slack():
    print('updates from slack')
    actual_one_day_ago = measure_date()
    slack_users = slack_client.api_call('users.list')['members']
    print(len(slack_users))
    people = People.query.filter_by(slack_handle=None).all()
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
            db.session.commit()
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
    messages = Messages.query.all()
    for m in messages:
        print(f'm = {m.id}')
        for x in range(0, m.number_of_sends):
            send_day = ''
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
                save_send_message(employee_id, m.id, x, send_date_time)
            elif m.country == 'CA' and my_country == 'CA':
                save_send_message(employee_id, m.id, x, send_date_time)
            elif m.country == 'ALL':
                save_send_message(employee_id, m.id, x, send_date_time)
            else:
                app.logger.info('No message to be sent, user country {} and message country {}'
                                .format(my_country, m.country))


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
    # to_send = Send()
    # to_send.emp_id = emp_id
    # to_send.message_id = message_id
    # to_send.send_order = send_order
    # to_send.send_dttm = send_dttm
    # to_send.last_updated = datetime.datetime.now()
    # to_send.save()
    dnow = datetime.datetime.utcnow()
    to_send = Send(emp_id=emp_id, message_id=message_id, send_dttm=send_dttm,
                      send_order=send_order, send_status=False, cancel_status=False,
                      last_updated=dnow, created_date=dnow)
    db.session.add(to_send)
    db.session.commit()


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


def search_messages(search_string, message):
    """
    Search message for text or titles that match the search string
    :param search_string:
    :param message:
    :return:
    """
    result = [x.strip() for x in search_string.split(' ')]
    print(f'tags {message.tags}')
    print(f'result {result}')
    for r in result:
        print(f'r {r}')
        for m in message.tags:
            if r.lower() in m.lower():
                return message


def send_opt_out_message(channel):
    message_attachments = []
    message_attach = {
        "callback_id": "opt_out",
        "replace_original": False,
        "delete_original": False,
        "fallback": "You need to upgrade your Slack client to receive this message.",
        "color": "#d72b3f",
        "actions": [{
            "name": "optout",
            "type": "button",
            "style": "danger",
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
        channel=channel,
        text='We\'re sad to hear things aren\'t going well. \n\n '
             'If you would like to opt-out of future messages, '
             'click the button below.',
        attachments=message_attachments
    )


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
    # send = Send.objects(Q(send_dttm__lte=now) & Q(send_dttm__gte=lasthour) & Q(send_status__exact=False))
    send = Send.query.filter(Send.send_dttm < now, Send.send_dttm > lasthour,
                                Send.send_status is False).all()
    slack_client.rtm_connect()
    users = slack_client.api_call('users.list')['members']
    for s in send:
        print('new hire messages ={}'.format(s['send_status']))
        print(f'emp {s["emp_id"]}')
        emp = People.query.filter_by(emp_id=s['emp_id']).first()
        if emp.user_opt_out is False and emp.manager_opt_out is False and emp.admin_opt_out is False:
            # message = Messages.objects(Q(id=s['message_id'])).get().to_mongo()
            message = Messages.get(s['message_id'])
            print('emp = {}'.format(emp))
            print('message = {}'.format(message))
            message_user = emp['slack_handle']
            user = search(users, 'name', message_user)
            if user is not None:
                dm = slack_client.api_call(
                    'im.open',
                    user=user['id'],
                )['channel']['id']
                send_dm_message(dm, message)
                s.update(set__send_status=True)
        else:
            s.update(set__cancel_status=True)
            print('User has opted out of notifications')


def send_dm_message(dm, message):
    print(f'send message {message}')
    message_text = message.text.split('button:')
    message_link = message.title_link
    message_attachments = []
    callback = message.title.lower()
    if len(message_link) > 0:
        print(f'message link {message_link}')
        message_actions = []
        for x in message_link:
            print(f'url {x["url"]}')
            action = {
                "type": "button",
                "text": x['name'],
                "name": x['name'],
                "style": "primary",
                "url": x['url'],
                "value": x['url']
            }
            message_actions.append(action)
        message_attach = {
            "callback_id": callback,
            "fallback": "You need to upgrade your Slack client to receive this message.",
            "color": "#008952",
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


def get_user_info():
    """
    Get user session for browser
    :return:
    """
    user = None
    if session.get('profile'):
        user = {'userid': session.get('profile')['user_id'], 'username': session.get('profile')['name'],
                'picture': session.get('profile')['picture']}
    return user


@app.route('/profile', methods=['GET', 'POST'])
@requires_auth
def profile():
    logger.info("User: {} authenticated proceeding to dashboard.".format(session.get('profile')['user_id']))
    user = get_user_info()
    admin = get_user_admin()
    form = AddAdminRequest(request.form)
    print(json.dumps(session['jwt_payload']["https://sso.mozilla.com/claim/groups"]))
    print(json.dumps(session['jwt_payload']))
    person = People.query.filter_by(emp_id=session['profile']['user_id']).first()
    roles = AdminRoles.query.all()
    role_names = [(role.role_name, role.role_description) for role in roles]
    form.roles.choices = role_names
    print(f'person {person}')
    if request.method == 'POST':
        if form.validate():
            requested_roles = form.roles.data
            print(f'roles = {requested_roles}')
            person.admin_role_requested = requested_roles
            person.admin_requested = True
            person.admin_requested_date = datetime.datetime.utcnow()
            person.admin_status = 'Pending'
            db.session.commit()
            slack_client.api_call(
                'chat.postMessage',
                channel='GE97V74BD',
                text=f'{person.first_name} {person.last_name} has requested to be granted the '
                     f'following role(s) {requested_roles}.')
    return render_template('profile.html',
                           userinfo=session['profile'],
                           usergroups=session['jwt_payload']["https://sso.mozilla.com/claim/groups"],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4), user=user, admin=admin,
                           person=person, roles=roles, form=form)


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


@app.route('/logout', host='https://newbie.ngrok.io')
def logout():
    """
    Logout and clear session
    :return:
    """
    # Clear session stored data
    session.clear()
    return redirect('https://newbie.ngrok.io/')


@app.route('/', host='https://newbie.ngrok.io')
def index():
    """
    Home page route
    :return: Home page
    """
    print('session {}'.format(session.get('profile')))
    user = get_user_info()
    admin = get_user_admin()
    print(f'user {user}')
    print(f'admin {admin}')
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
    messages = Messages.query.all()
    if request.method == 'POST':
        if form.validate():
            title_link = json.loads(form.linkitems.data)
            date_start = form.send_date.data.split('-')
            sdate = datetime.datetime(int(date_start[0]), int(date_start[1]), int(date_start[2]), 0, 0, 0)
            send_date = datetime.datetime.strftime(sdate, '%Y-%m-%dT%H:%M:%S')
            send_once = True if form.send_once.data is True else False
            tagitems = form.tagitems.data
            tag = tagitems.split('|')
            message = Messages(type=form.message_type.data, category=form.category.data, title=form.title.data,
                                  title_link=title_link, send_day=form.send_day.data, send_hour=form.send_time.data,
                                  send_date=send_date, send_once=send_once, frequency=form.frequency.data,
                                  text=form.text.data, number_of_sends=form.number_of_sends.data, country=form.country.data,
                                  tags=tag[:-1])
            db.session.add(message)
            db.session.commit()
            # return redirect(current_host + '/addMessage')
            return redirect(url_for('add_new_message'))
        else:
            print('errors = {}'.format(form.errors))
            return redirect(url_for('add_new_message'))
    return render_template('messages.html', messages=messages, form=form, user=user, admin=admin)


@app.route('/editMessage/<int:message_id>', methods=['GET', 'POST'])
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
    messages = Messages.query.get_or_404(message_id)
    if request.method == 'GET':
        # messages = Messages.objects(Q(id=message_id)).get()
        form.message_type.data = messages.type
        form.category.data = messages.category
        form.title.data = messages.title
        form.linkitems.data = messages.title_link
        form.send_day.data = messages.send_day
        form.send_time.data = messages.send_hour
        form.send_date.data = messages.send_date
        form.send_once.data = messages.send_once
        form.frequency.data = messages.frequency
        form.text.data = messages.text
        form.number_of_sends.data = messages.number_of_sends
        form.country.data = messages.country
        form.tagitems.data = messages.tags
        return render_template('message_edit.html', form=form, user=user, admin=admin, message=messages)
    elif request.method == 'POST':
        if form.validate():
            messages.type = form.message_type.data
            messages.category = form.category.data
            messages.title = form.title.data
            messages.title_link = json.loads(form.linkitems.data)
            messages.send_day = form.send_day.data
            messages.send_hour = form.send_time.data
            date_start = form.send_date.data.split('-')
            sdate = datetime.datetime(int(date_start[0]), int(date_start[1]), int(date_start[2]), 0, 0, 0)
            messages.send_date = datetime.datetime.strftime(sdate, '%Y-%m-%dT%H:%M:%S')
            messages.send_once = True if form.send_once.data is True else False
            messages.frequency = form.frequency.data
            messages.text = form.text.data
            messages.number_of_sends = form.number_of_sends.data
            messages.country = form.country.data
            tagitems = form.tagitems.data
            tag = tagitems.split('|')
            tag = [re.sub(r'\r\n\s+', '', x) for x in tag]
            messages.tags = tag[:-1]
            db.session.commit()
            if current_host:
                return redirect(current_host + '/addMessage')
            return redirect(url_for('add_new_message'))
        else:
            print('errors = {}'.format(form.errors))
            if current_host:
                return redirect(current_host + '/addMessage')
            return redirect(url_for('add_new_message'))


@app.route('/deleteMessage/<int:message_id>', methods=['POST'])
@requires_admin
def delete_message(message_id):
    """
    Delete message from database
    :param message_id:
    :return:
    """
    messages = Messages.query.get_or_404(message_id)
    db.session.delete(messages)
    db.session.commit()
    if current_host:
        return redirect(current_host + '/addMessage')
    return redirect(url_for('add_new_message'))


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
            date_start = form.start_date.data.split('-')
            sdate = datetime.datetime(int(date_start[0]), int(date_start[1]), int(date_start[2]), 0, 0, 0)
            last_updated = datetime.datetime.now()
            start_date = datetime.datetime.strftime(sdate, '%Y-%m-%dT%H:%M:%S')
            person = People(emp_id=form.emp_id.data, first_name=form.first_name.data, last_name=form.last_name.data,
                               email=form.email.data, slack_handle=form.slack_handle.data, start_date=start_date,
                               last_modified=last_updated, timezone=form.timezone.data, country=form.country.data,
                               manager_id=form.manager_id.data, user_opt_out=False, manager_opt_out=False,
                               admin_opt_out=False, created_date=last_updated)
            db.session.add(person)
            try:
                db.session.commit()
            except IntegrityError as error:
                print('DuplicateKeyError {}'.format(error))
                db.session.rollback()
            newly_added_user = People.query.filter_by(emp_id=form.emp_id.data).first()
            print('newly added user = {}'.format(newly_added_user.first_name))
            add_messages_to_send(newly_added_user)
            if current_host:
                return redirect(current_host + '/addEmployee')
            return redirect(url_for('add_new_employee'))
        else:
            print('errors = {}'.format(form.errors))
            return render_template('employees.html', employees=None, form=form, selectedEmp=None,  timezones=all_timezones, user=user, admin=admins)
    else:
        admin = user['userid'].split('|')
        admin = admin[2]

        employees = []
        employee_list = People.query.all()

        user_id = session.get('profile')['user_id']
        admin_data = Admin.query.filter_by(emp_id=user_id).first()
        if admin_data.super_admin:
            employees = employee_list
        else:
            for emp in employee_list:
                if re.findall(admin, emp.manager_id):
                    employees.append(emp)
        return render_template('employees.html', employees=employees, form=form, selectedEmp=None,  timezones=all_timezones, user=user, admin=admins)


@app.route('/deleteEmployee/<int:emp_id>')
@requires_super
def delete_employee(emp_id):
    """
    Delete employee from database
    :param emp_id:
    :return:
    """
    person = People.query.get_or_404(emp_id)
    messages = Send.query.filter_by(emp_id=person.emp_id).all()
    for mes in messages:
        db.session.delete(mes)
    db.session.delete(person)
    db.session.commit()
    if current_host:
        return redirect(current_host + '/addEmployee')
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
    pending_form = PendingRequestsForm(request.form)
    admin_roles = AdminRoles.query.all()
    admin = get_user_admin()
    peoples = People.query.all()
    global admin_people
    admin_people = peoples
    role_names = [(role.role_name, role.role_description) for role in admin_roles]
    admin_form.roles.choices = role_names
    admins = Admin.query.all()
    user = get_user_info()
    pending_requests = People.query.filter_by(admin_status='Pending').all()
    print(f'pending requests {pending_requests}')
    return render_template('admin.html', user=user, admin_roles=admin_roles, admins=admins, form=form,
                           admin_form=admin_form, people=peoples, admin=admin, pending_requests=pending_requests, pending_form=pending_form)


@app.route('/adminRequest/<int:person_id>', methods=['POST'])
@requires_super
def admin_request(person_id):
    pending_form = PendingRequestsForm(request.form)
    person = People.query.get_or_404(person_id)
    if request.method == 'POST':
        if pending_form.validate():
            decision = pending_form.decision.data
            comment = pending_form.comment.data
            if decision == 'approve':
                name = person.first_name + ' ' + person.last_name
                super_admin = False
                if 'Super Admin' in person.admin_role_requested:
                    super_admin = True
                new_admin = Admin(emp_id=person.emp_id, name=name, super_admin=super_admin, roles=person.admin_role_requested)
                db.session.add(new_admin)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
            person = People.query.get_or_404(person_id)
            person.admin_status = decision.capitalize()
            person.admin_status_updated_date = datetime.datetime.utcnow()
            current_admin = People.query.filter_by(emp_id=session.get('profile')['user_id']).first()
            person.admin_request_updated_by = current_admin.id
            db.session.commit()
            if current_host:
                return redirect(current_host + '/admin')
            return redirect(url_for('admin_page'))


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
            role = AdminRoles(role_name=form.role_name.data, role_description=form.role_description.data)
            db.session.add(role)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            if current_host:
                return redirect(current_host + '/admin')
            return redirect(url_for('admin_page'))
        else:
            if current_host:
                return redirect(current_host + '/admin')
            return redirect(url_for('admin_page'))
    else:
        if current_host:
            return redirect(current_host + '/admin')
        return redirect(url_for('admin_page'))


@app.route('/deleteRole/<int:role_id>', methods=['POST'])
@requires_super
def delete_role(role_id):
    """
    Delete employee from database
    :param role_name:
    :return:
    """
    role = AdminRoles.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    if current_host:
        return redirect(current_host + '/admin')
    return redirect(url_for('admin_page'))


@app.route('/adminUser', methods=['POST'])
@requires_super
def admin_user():
    """
    Add admin user to database
    :return:
    """
    admin_form = AddAdminForm(request.form)
    admin_roles = AdminRoles.query.all()
    role_names = [(role.role_name, role.role_description) for role in admin_roles]
    role_names = role_names[1:]
    print(f'admin people {admin_people[11]}')
    admin_form.roles.choices = role_names
    if request.method == 'POST':
        print('admin form {}'.format(admin_form.roles.data))
        if admin_form.validate():
            try:
                print(f'selected admin {admin_form.emp_id.data}')
                selected_admin = admin_form.emp_id.data.split(' ')
                name = ' '.join(selected_admin[1:])
                admin = Admin(emp_id=selected_admin[0], name=name, super_admin=admin_form.super_admin.data,
                                 roles=admin_form.roles.data)
                db.session.add(admin)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
            except:
                print('unable to save admin')
            if current_host:
                return redirect(current_host + '/admin')
            return redirect(url_for('admin_page'))
        else:
            print('errors = {}'.format(admin_form.errors))
            if current_host:
                return redirect(current_host + '/admin')
            return redirect(url_for('admin_page'))
    else:
        print('errors = {}'.format(admin_form.errors))
        if current_host:
            return redirect(current_host + '/admin')
        return redirect(url_for('admin_page'))


@app.route('/deleteAdmin/<int:admin_id>', methods=['POST'])
@requires_super
def delete_admin(admin_id):
    """
    Delete employee from database
    :param admin_id:
    :return:
    """
    admin = Admin.query.get_or_404(admin_id)
    db.session.delete(admin)
    db.session.commit()
    if current_host:
        return redirect(current_host + '/admin')
    return redirect(url_for('admin_page'))


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
                # People.objects(Q(slack_handle=user)).update(set__user_opt_out=False)
                person = People.query.filter_by(slack_handle=user)
                person.user_opt_out = False
                db.session.commit()
                slack_call_api('chat.update', form_json['channel']['id'], form_json['message_ts'], message_text,
                               '')
            elif 'stop' in actions.lower():
                print('stop')
                message_text = 'We\'ve unsubscribed you from onboarding messages.'
                # People.objects(Q(slack_handle=user)).update(set__user_opt_out=True)
                person = People.query.filter_by(slack_handle=user)
                person.user_opt_out = True
                db.session.commit()
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
                feedback = UserFeedback(emp_id=form_json['user']['name'], rating='thumbsup', comment='')
                db.session.add(feedback)
                db.session.commit()
                slack_client.api_call(
                    "dialog.open",
                    trigger_id=form_json["trigger_id"],
                    dialog=message_attachments
                )

                return make_response('', 200)
            elif 'thumbsdown' in actions.lower():
                print('thumbsdown')
                message_attachments['state'] = 'thumbsdown'
                feedback = UserFeedback(emp_id=form_json['user']['name'], rating='thumbsdown', comment='')
                db.session.add(feedback)
                db.session.commit()
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
        feedback = UserFeedback.query.filter_by(emp_id=form_json['user']['name']).all()
        created = feedback[len(feedback) - 1].created_date
        for feed in feedback:
            if feed.created_date == created:
                feed.comment = form_json['submission']['comment']
                db.session.commit()
        if form_json['state'] == 'thumbsdown':
            channel = form_json['channel']['id']
            send_opt_out_message(channel)
        else:
            slack_client.api_call(
                'chat.postMessage',
                channel=form_json['channel']['id'],
                text='Thanks for your feedback!',
                )
        return make_response('', 200)


@app.route('/slack/newbiesearch', methods=['GET', 'POST'])
def newbie_search():
    """
    Slack slash newbiesearch - performs search for topic that is inserted after the
    slash command.
    :return: Message sent with list of topics that are related to the search criteria
    """
    incoming_search_term = json.dumps(request.values['text']).replace('"', '')
    print(f'incoming search {incoming_search_term}')
    user = json.dumps(request.values['user_name'])
    user = user.replace('"', '')
    print(f'searching user {user}')
    messages = Messages.query.all()
    found_messages = []
    for message in messages:
        searchresult = search_messages(incoming_search_term, message)
        if searchresult is not None:
            found_messages.append(searchresult)
    print(f'found messages {found_messages}')
    for found in found_messages:
        if user is not None:
            dm = request.values['channel_id']
            send_dm_message(dm, found)
    if len(found_messages) == 0:
        return make_response('I\'m sorry, I couldn\'t find '
                      'any information on ' + incoming_search_term, 200)
    return make_response('', 200)


@app.route('/slack/newhirehelp', methods=['POST'])
def new_hire_help():
    """
    Slack slash newhbie - performs action based on slash message commands
    :return: Message sent to update user on action of slash command
    """
    incoming_message = json.dumps(request.values['text']).replace('"', '')
    user = json.dumps(request.values['user_name'])
    user = user.replace('"','')
    print(f'user {user}')
    if incoming_message == 'opt-in':
        # People.objects(Q(slack_handle=user)).update(set__user_opt_out=False)
        person = People.query.filter_by(slack_handle=user)
        person.user_opt_out = False
        db.session.commit()
        message_response = "Welcome back! You'll receive any scheduled notifications."
    elif incoming_message == 'help':
        message_response = "To explore how I can help you, try using the slash command for " \
                           "searching my topics.  It's easy, just type /newbiesearch followed" \
                           "by the topic that you need more information on.  I'll respond " \
                           "with any relevant information I find."
    elif incoming_message == 'opt-out':
        channel = request.values['channel_id']
        send_opt_out_message(channel)
        message_response = ''
        # People.objects(Q(slack_handle=user)).update(set__user_opt_out=True)
        # message_response = 'Okay, we\'ll stop sending you important tips and reminders. ' \
        #                    'Hope you don\'t miss any deadlines!'
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
    print(f'slack user {users}')
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


