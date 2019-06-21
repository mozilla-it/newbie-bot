import logging
import slackclient
import datetime
from newb.models import People, AuthGroups, Messages, Admin, MessagesToSend as Send, db
from newb import settings
from werkzeug.exceptions import NotFound
from authzero import AuthZero
import pytz
from dateutil.relativedelta import relativedelta
import holidays
from sqlalchemy.exc import IntegrityError

us_holidays = holidays.US()
ca_holidays = holidays.CA()

slack_client = slackclient.SlackClient(settings.SLACK_BOT_TOKEN)
client_id = settings.CLIENT_ID
client_secret = settings.CLIENT_ID
client_uri = settings.CLIENT_URI

def send_newhire_messages():
    """
    Send new hires messages, this process is ran on a schedule
    :return:
    """
    print('send newhire messages')
    now = datetime.datetime.utcnow()
    lasthour = now - datetime.timedelta(minutes=59, seconds=59, days=7)
    send = Send.query.filter(Send.send_dttm > lasthour).filter(Send.send_dttm < now).filter(Send.send_status.is_(False))\
        .filter(Send.cancel_status.is_(False))
    slack_client.rtm_connect()
    users = slack_client.api_call('users.list')['members']
    for s in send:
        emp = People.query.filter_by(emp_id=s.emp_id).first()
        if emp.user_opt_out is False and emp.manager_opt_out is False and emp.admin_opt_out is False:
            try:
                message = Messages.query.get_or_404(s.message_id)
                message_user = emp.slack_handle
                user = search(users, 'name', message_user)
                if user is not None:
                    dm = slack_client.api_call(
                        'im.open',
                        user=user['id'],
                    )['channel']['id']
                    send_dm_message(dm, message)
                    s.send_status = True
                    s.last_updated = datetime.datetime.utcnow()
                    db.session.commit()
            except NotFound as e:
                logging.error(f'NotFound {e}')
                s.send_status = True
                s.last_updated = datetime.datetime.utcnow()
                db.session.commit()
        else:
            s.cancel_status = True
            db.session.commit()
            print('User has opted out of notifications')


def search(dict_list, key, value):
    for item in dict_list:
        if item[key] == value:
            return item


def send_dm_message(dm, message):
    print(f'send message {message}')
    message_text = message.text.split('button:')
    message_link = message.title_link
    message_attachments = []
    callback = message.topic.lower()
    if len(message_link) > 0:
        message_actions = []
        for x in message_link:
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
    else:
        logging.info('No message attachments.')

    slack_client.api_call(
        'chat.postMessage',
        channel=dm,
        text=message_text[0],
        attachments=message_attachments
    )


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
                                "user_metadata.groups,userinfo,app_metadata.groups,app_metadata.hris,"
                                "app_metadata")
    for user in users:
        if 'app_metadata' in user:
            groups = user["app_metadata"]["groups"]
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
            # print(f'auth0 user {user}')
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
    peoples = People.query.filter_by(slack_handle=None).all()
    for person in peoples:
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
            person.last_modified = datetime.datetime.utcnow()
            db.session.commit()
            print(actual_one_day_ago)
            start_date = person.start_date
            # .strptime('%Y-%m-%d')
            print('start_date {}'.format(start_date))
            print(start_date > actual_one_day_ago)
            if start_date > actual_one_day_ago:
                print('start date within 30 days {}'.format(start_date > actual_one_day_ago))
                add_messages_to_send(person)


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
        send_day = m.send_day
        if m.send_once:
            send_date_time = m.send_date
        else:
            send_date_time = start_date + datetime.timedelta(days=send_day)
        send_date_time = my_timezone.localize(send_date_time)
        send_date_time = send_date_time.replace(hour=m.send_hour, minute=0, second=0)
        send_date_time = adjust_send_date_for_holidays_and_weekends(send_date_time, my_country)
        utc = pytz.UTC
        send_date_time = send_date_time.astimezone(utc)
        if m.country == 'US' and my_country == 'US':
            save_send_message(employee_id, m.id, 0, send_date_time)
        elif m.country == 'CA' and my_country == 'CA':
            save_send_message(employee_id, m.id, 0, send_date_time)
        elif m.country == 'ALL':
            if m.repeatable:
                spin_out_repeats(employee_id, m.id, m.repeat_type, m.repeat_number, m.repeat_times, send_date_time)
            else:
                save_send_message(employee_id, m.id, 0, send_date_time)
        else:
            logging.info(f'No message to be sent, user country {my_country} and message country {m.country} for message {m.id}')


def save_send_message(emp_id, message_id, send_order, send_dttm):
    """
    Save to Messages to Send table
    :param emp_id:
    :param message_id:
    :param send_order:
    :param send_dttm:
    :return:
    """
    dnow = datetime.datetime.utcnow()
    send_dttm = send_dttm.replace(tzinfo=None)
    to_send = Send(emp_id=emp_id, message_id=message_id, send_dttm=send_dttm, send_order=send_order, send_status=False,
                   cancel_status=False, last_updated=dnow, created_date=dnow)
    db.session.add(to_send)
    db.session.commit()


def spin_out_repeats(employee_id, message_id, message_type, number, times, current_send_date):
    for x in range(0, times):
        save_send_message(employee_id, message_id, 0, current_send_date)
        if message_type == 'week':
            week_num = number * 7
            date_increment = datetime.timedelta(days=week_num)
            current_send_date = current_send_date + date_increment
        elif message_type == 'month':
            date_increment = relativedelta(months=+number)
            current_send_date = current_send_date + date_increment
        elif message_type == 'year':
            date_increment = relativedelta(years=+number)
            current_send_date = current_send_date + date_increment


def adjust_send_date_for_holidays_and_weekends(send_date_time, country):
    """"
    Adjust date to non-holiday or weekend
    :param send_date_time
    :param country
    :return send_date_teime
    """
    weekday = send_date_time.weekday()
    if weekday > 4:
        if weekday == 6:
            send_date_time = send_date_time + datetime.timedelta(days=1)
        else:
            send_date_time = send_date_time + datetime.timedelta(days=2)
        adjust_send_date_for_holidays_and_weekends(send_date_time, country)
    if country == 'US':
        if send_date_time in us_holidays:
            send_date_time = send_date_time + datetime.timedelta(days=1)
            adjust_send_date_for_holidays_and_weekends(send_date_time, country)
    if country == 'CA':
        if send_date_time in ca_holidays:
            send_date_time = send_date_time + datetime.timedelta(days=1)
            adjust_send_date_for_holidays_and_weekends(send_date_time, country)
    return send_date_time


def searchemail(dict_list, key, value):
    for item in dict_list:
        try:
            if item['profile'][key] == value:
                return item
        except:
            pass


def measure_date():
    current_day = datetime.datetime.today()
    thirty_days_ago = datetime.timedelta(days=31)
    actual_thirty_days_ago = datetime.datetime.strptime(
        datetime.datetime.strftime(current_day - thirty_days_ago, '%Y-%m-%d'), '%Y-%m-%d')
    return actual_thirty_days_ago
