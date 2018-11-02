import mongoengine
import datetime


class Admin(mongoengine.Document):
    emp_id = mongoengine.StringField(required=True, unique=True)
    name = mongoengine.StringField(required=True)
    super_admin = mongoengine.BooleanField(default=False)
    roles = mongoengine.StringField(required=True)
    created_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'core',
        'collection': 'admin'
    }
