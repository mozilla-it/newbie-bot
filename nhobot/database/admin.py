import mongoengine
import datetime

from nhobot import db

class Admin(mongoengine.Document):
    emp_id = mongoengine.StringField(required=True, unique=True)
    name = mongoengine.StringField(required=True)
    super_admin = mongoengine.BooleanField(default=False)
    roles = mongoengine.ListField()
    created_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'core',
        'collection': 'admin'
    }

class NewAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(), unique=True, )