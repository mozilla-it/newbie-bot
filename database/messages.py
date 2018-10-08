import mongoengine
import datetime

class Messages(mongoengine.Document):
    message_id = mongoengine.IntField(unique=True, required=True)
    type = mongoengine.StringField(required=True)
    category = mongoengine.StringField(required=True)
    title = mongoengine.StringField(required=True)
    title_link = mongoengine.StringField()
    send_day = mongoengine.IntField(required=True)
    send_hour = mongoengine.IntField(required=True)
    frequency = mongoengine.StringField(required=True)
    number_of_sends = mongoengine.IntField(required=True, default=1)
    text = mongoengine.StringField(required=True)
    created_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'core',
        'collection': 'messages'
    }