import mongoengine
import datetime


class UserFeedback(mongoengine.Document):
    action = mongoengine.StringField()
    emp_id = mongoengine.StringField(required=True)
    rating = mongoengine.StringField()
    comment = mongoengine.StringField(max_length=3000)
    created_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'core',
        'collection': 'user_feedback'
    }
