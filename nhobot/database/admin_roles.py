import mongoengine
import datetime


class AdminRoles(mongoengine.Document):
    role_name = mongoengine.StringField(required=True, unique=True)
    role_description = mongoengine.StringField(required=True)
    created_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'core',
        'collection': 'admin_roles'
    }
