import mongoengine
import datetime

class MessagesToSend(mongoengine.Document):
    emp_id = mongoengine.StringField(required=True, unique=False)
    message_id = mongoengine.StringField(required=True)
    send_dttm = mongoengine.DateTimeField()
    send_order = mongoengine.IntField(required=True)
    send_status = mongoengine.BooleanField(required=True, default=False)
    cancel_status = mongoengine.BooleanField(required=True, default=False)
    last_updated = mongoengine.DateTimeField(required=True)
    created_dt = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'core',
        'collection': 'messages_to_send'
    }