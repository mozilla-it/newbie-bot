import datetime
from nhobot import db


class UserFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(10), nullable=False)
    emp_id = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.String(10), nullable=False)
    comment = db.Column(db.String(300), nullable=True)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"UserFeedback('{self.action}', '{self.emp_id}', '{self.rating}', '{self.comment}'," \
            f"'{self.created_date}')"
