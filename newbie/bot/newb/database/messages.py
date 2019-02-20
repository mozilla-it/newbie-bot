import datetime
from newb import db
from sqlalchemy import String, ARRAY, JSON


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32), nullable=False)
    # category = db.Column(db.String(32), nullable=False)
    topic = db.Column(db.String(100), unique=True, nullable=False)
    title_link = db.Column(JSON, nullable=True)
    send_day = db.Column(db.Integer, nullable=True)
    send_hour = db.Column(db.Integer, nullable=True)
    repeatable = db.Column(db.Boolean, default=False)
    repeat_number = db.Column(db.Integer())
    repeat_type = db.Column(db.String(6))
    repeat_times = db.Column(db.Integer())
    text = db.Column(db.String(999), nullable=False)
    send_date = db.Column(db.DateTime, nullable=False)
    send_once = db.Column(db.Boolean, default=True, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    country = db.Column(db.String(1000), nullable=False, default='ALL')
    callback_id = db.Column(db.String(15), nullable=True)
    tags = db.Column(ARRAY(String))
    team = db.Column(db.String(100), nullable=True, default='HR')
    # topic = db.Column(db.String(50), nullable=True, default='ALL')
    owner = db.Column(db.String(50), nullable=True, default='Mozilla')
    location = db.Column(db.String(1000), nullable=True, default='Mozilla')
    emp_type = db.Column(db.String(1000), nullable=True, default='FTE')

    def __repr__(self):
        return f"Messages('{self.type}', '{self.topic}', '{self.title_link}'" \
            f"'{self.send_day}', '{self.send_hour}', " \
            f"'{self.text}', '{self.send_date}', '{self.created_date}', '{self.country}', " \
            f"'{self.callback_id}', '{self.tags}', '{self.team}', '{self.owner}', '{self.location}', '{self.emp_type}')"
