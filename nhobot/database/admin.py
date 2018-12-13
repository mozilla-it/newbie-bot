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
    emp_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    super_admin = db.Column(db.Boolean, default=False)
    roles = db.Column(db.String(1000))
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"NewAdmin('{self.emp_id}', '{self.name}', '{self.super_admin}', '{self.roles}', '{self.created_date}')"
