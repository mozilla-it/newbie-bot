import mongoengine
import datetime

class People(mongoengine.Document):
    emp_id = mongoengine.StringField(required=True, unique=True)
    first_name = mongoengine.StringField(required=True)
    last_name = mongoengine.StringField(required=True)
    email = mongoengine.StringField()
    slack_handle = mongoengine.StringField()
    start_date = mongoengine.DateTimeField()
    last_modified = mongoengine.DateTimeField()
    timezone = mongoengine.StringField()
    country = mongoengine.StringField()
    manager_id = mongoengine.StringField()
    user_opt_out = mongoengine.BooleanField(default=False)
    manager_opt_out = mongoengine.BooleanField(default=False)
    admin_opt_out = mongoengine.BooleanField(default=False)
    created_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'core',
        'collection': 'people'
    }
