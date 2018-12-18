import bson
from nhobot.database.people import NewPeople
from nhobot.database.messages import NewMessages
from nhobot.database.messages_to_send import NewMessagesToSend as NewSend
from nhobot.database.admin import NewAdmin
from nhobot.database.admin_roles import NewAdminRoles
from nhobot.database.user_feedback import NewUserFeedback
from nhobot import db
import datetime
dnow = datetime.datetime.utcnow()
import json

# Convert Admins
# with open('/Users/marty331/Dev/nhobot/admin.bson', 'rb') as f:
#     data = bson.decode_all(f.read())
#     for d in data:
#         admin = NewAdmin(emp_id=d['emp_id'], name=d['name'], super_admin=d['super_admin'], roles=d['roles'])
#         db.session.add(admin)
#     db.session.commit()

# Convert Roles
# with open('/Users/marty331/Dev/nhobot/admin_roles.bson', 'rb') as f:
#     data = bson.decode_all(f.read())
#     for d in data:
#         role = NewAdminRoles(role_name=d['role_name'], role_description=d['role_description'])
#         db.session.add(role)
#     db.session.commit()

# Convert People
# with open('/Users/marty331/Dev/nhobot/people.bson', 'rb') as f:
#     data = bson.decode_all(f.read())
#     for d in data:
#         if len(d['first_name']) <31 and len(d['last_name']) < 31:
#             slack = ''
#             if 'slack_handle' in d:
#                 slack = d['slack_handle']
#                 print(f'slack {d["slack_handle"]}')
#             timezone = 'US/Pacific'
#             if 'timezone' in d:
#                 timezone = d['timezone']
#             country = 'US'
#             if 'country' in d:
#                 country = d['country']
#                 print(f'country {country}')
#             person = NewPeople(emp_id=d['emp_id'], first_name=d['first_name'], last_name=d['last_name'],
#                                email=d['email'],
#                                slack_handle=slack, start_date=d['start_date'], last_modified=dnow,
#                                timezone=timezone, country=country, manager_id=d['manager_id'],
#                                user_opt_out=d['user_opt_out'], manager_opt_out=d['manager_opt_out'],
#                                admin_opt_out=d['admin_opt_out'], created_date=dnow)
#             db.session.add(person)
#     db.session.commit()

# Convert Messages
with open('/Users/marty331/Dev/nhobot/messages.bson', 'rb') as f:
    data = bson.decode_all(f.read())
    for d in data:
        links = d["title_link"]
        callback = ''
        if "callback_id" in d:
            callback = d["callback_id"]
        message = NewMessages(type=d['type'], category=d['category'], title=d['title'], title_link=links,
                              send_day=d['send_day'], send_hour=d['send_hour'], frequency=d['frequency'],
                              number_of_sends=d['number_of_sends'], text=d['text'], send_date=d['send_date'],
                              send_once=d['send_once'], created_date=dnow, country=d['country'],
                              callback_id=callback, tags=d['tags'])
        db.session.add(message)
    db.session.commit()
