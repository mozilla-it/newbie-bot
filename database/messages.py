import mongoengine
import datetime

class Messages(mongoengine.Document):
    type = mongoengine.StringField(required=True)
    category = mongoengine.StringField(required=True)
    title = mongoengine.StringField(unique=True, required=True)
    title_link = mongoengine.StringField()
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

    meta = {
        'db_alias': 'core',
        'collection': 'messages'
    }