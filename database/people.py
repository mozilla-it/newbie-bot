import mongoengine
import datetime

class People(mongoengine.Document):
    emp_id = mongoengine.IntField(required=True, unique=True)
    first_name = mongoengine.StringField(required=True)
    last_name = mongoengine.StringField(required=True)
    slack_handle = mongoengine.StringField()
    start_date = mongoengine.StringField()
    user_opt_out = mongoengine.BooleanField(default=False)
    manager_opt_out = mongoengine.BooleanField(default=False)
    admin_opt_out = mongoengine.BooleanField(default=False)
    created_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'core',
        'collection': 'people'
    }