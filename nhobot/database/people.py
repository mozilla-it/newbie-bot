import datetime
from nhobot import db


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    slack_handle = db.Column(db.String(50), nullable=True, default='')
    start_date = db.Column(db.DateTime, nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    timezone = db.Column(db.String(100), nullable=True, default='US/Pacific')
    country = db.Column(db.String(4), nullable=True)
    manager_id = db.Column(db.String(120), nullable=False)
    user_opt_out = db.Column(db.Boolean, nullable=False, default=False)
    manager_opt_out = db.Column(db.Boolean, nullable=False, default=False)
    admin_opt_out = db.Column(db.Boolean, nullable=False, default=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"NewMessagesToSend('{self.emp_id}', '{self.first_name}', '{self.last_name}', " \
            f"'{self.email}', '{self.slack_handle}', '{self.start_date}', '{self.last_modified}'," \
            f"'{self.timezone}', '{self.country}', '{self.manager_id}', '{self.manager_opt_out}', " \
            f"'{self.user_opt_out}', '{self.admin_opt_out}', '{self.created_date}')"
