import mongoengine
import datetime
from nhobot import db


class AdminRoles(mongoengine.Document):
    role_name = mongoengine.StringField(required=True, unique=True)
    role_description = mongoengine.StringField(required=True)
    created_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'core',
        'collection': 'admin_roles'
    }

class NewAdminRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), nullable=False, unique=True)
    role_description = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"NewAdminRoles('{self.role_name}', '{self.role_description}', '{self.created_date}')"
