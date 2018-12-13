import mongoengine
import datetime
from nhobot import db


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

class NewUserFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(10), nullable=False)
    emp_id = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.String(10), nullable=False)
    comment = db.Column(db.String(300), nullable=True)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"NewUserFeedback('{self.action}', '{self.emp_id}', '{self.rating}', '{self.comment}'," \
            f"'{self.created_date}')"
