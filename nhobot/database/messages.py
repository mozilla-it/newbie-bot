import mongoengine
import datetime
from nhobot import db

class Messages(mongoengine.Document):
    type = mongoengine.StringField(required=True)
    category = mongoengine.StringField(required=True)
    title = mongoengine.StringField(unique=True, required=True)
    title_link = mongoengine.ListField()
    send_day = mongoengine.IntField(required=True)
    send_hour = mongoengine.IntField(required=True)
    frequency = mongoengine.StringField(required=True)
    number_of_sends = mongoengine.IntField(required=True)
    text = mongoengine.StringField(required=True)
    send_date = mongoengine.DateTimeField()
    send_once = mongoengine.BooleanField(default=False)
    created_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    country = mongoengine.StringField(required=True)
    callback_id = mongoengine.StringField()
    tags = mongoengine.ListField()

    meta = {
        'db_alias': 'core',
        'collection': 'messages'
    }

class NewMessages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32), nullable=False)
    category = db.Column(db.String(32), nullable=False)
    title = db.Column(db.String(100), unique=True, nullable=False)
    title_link = db.Column(db.ARRAY(db.JSON), nullable=True)
    send_day = db.Column(db.Integer, nullable=True)
    send_hour = db.Column(db.Integer, nullable=True)
    frequency = db.Column(db.String(5))
    number_of_sends = db.Column(db.Integer)
    text = db.Column(db.String(999), nullable=False)
    send_date = db.Column(db.DateTime, nullable=False)
    send_once = db.Column(db.Boolean, default=True, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    country = db.Column(db.String(3), nullable=False, default='ALL')
    callback_id = db.Column(db.String(15), nullable=True)
    tags = db.Column(db.String())

    def __repr__(self):
        return f"NewMessages('{self.type}', '{self.category}', '{self.title}', '{self.title_link}'" \
            f"'{self.send_day}', '{self.send_hour}', '{self.frequency}', '{self.number_of_sends}', " \
            f"'{self.text}', '{self.send_date}', '{self.created_date}', '{self.country}', " \
            f"'{self.callback_id}', '{self.tags}')"
