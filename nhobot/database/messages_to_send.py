import mongoengine
import datetime
from nhobot import db

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

class NewMessagesToSend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(50), unique=True, nullable=False)
    message_id = db.Column(db.String(), nullable=False)
    send_dttm = db.Column(db.DateTime, nullable=False)
    send_order = db.Column(db.Integer, nullable=False)
    send_status = db.Column(db.Boolean, nullable=False, default=False)
    cancel_status = db.Column(db.Boolean, nullable=False, default=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"NewMessagesToSend('{self.emp_id}', '{self.message_id}', '{self.send_dttm}', " \
            f"'{self.send_order}', '{self.send_status}', '{self.cancel_status}', " \
            f"'{self.last_updated}', '{self.created_date}')"
