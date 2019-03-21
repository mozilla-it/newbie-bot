from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy import String, ARRAY, JSON
from sqlalchemy.inspection import inspect

db = SQLAlchemy()


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(150), nullable=False)
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
    admin_requested = db.Column(db.Boolean, default=False, nullable=True)
    admin_role_requested = db.Column(ARRAY(String), nullable=True)
    admin_requested_date = db.Column(db.DateTime, nullable=True)
    admin_status = db.Column(db.String, nullable=True)
    admin_status_updated_date = db.Column(db.DateTime, nullable=True)
    admin_request_updated_by = db.Column(db.Integer, nullable=True)
    admin_team = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"Person('{self.emp_id}', '{self.first_name}', '{self.last_name}', " \
            f"'{self.email}', '{self.slack_handle}', '{self.start_date}', '{self.last_modified}'," \
            f"'{self.timezone}', '{self.country}', '{self.manager_id}', '{self.manager_opt_out}', " \
            f"'{self.user_opt_out}', '{self.admin_opt_out}', '{self.created_date}'," \
               f"'{self.admin_requested}', '{self.admin_role_requested}', '{self.admin_requested_date}', '{self.admin_status}', '{self.admin_status_updated_date}'," \
               f"'{self.admin_request_updated_by}', '{self.admin_team}')"


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
        return f"Messages('{self.type}', '{self.topic}', '{self.title_link}', " \
            f"'{self.send_day}', '{self.send_hour}', " \
            f"'{self.text}', '{self.send_date}', '{self.created_date}', '{self.country}', " \
            f"'{self.callback_id}', '{self.tags}', '{self.team}', '{self.owner}', '{self.location}', '{self.emp_type}')"


class MessagesToSend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(50), unique=False, nullable=False)
    message_id = db.Column(db.String(), nullable=False)
    send_dttm = db.Column(db.DateTime(timezone=True), nullable=False)
    send_order = db.Column(db.Integer, nullable=False)
    send_status = db.Column(db.Boolean, nullable=False, default=False)
    cancel_status = db.Column(db.Boolean, nullable=False, default=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"MessagesToSend('{self.emp_id}', '{self.message_id}', '{self.send_dttm}', " \
            f"'{self.send_order}', '{self.send_status}', '{self.cancel_status}', " \
            f"'{self.last_updated}', '{self.created_date}')"


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


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    super_admin = db.Column(db.Boolean, default=False)
    roles = db.Column(db.String(1000))
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    team = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"Admin('{self.emp_id}', '{self.name}', '{self.super_admin}', '{self.roles}', '{self.created_date}', '{self.team}')"


class AdminRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), nullable=False, unique=True)
    role_description = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"AdminRoles('{self.role_name}', '{self.role_description}', '{self.created_date}')"


class AuthGroups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groups = db.Column(db.String(150), unique=True, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"AuthGroups('{self.groups}', {self.created_date}')"


class SearchTerms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String(100), unique=False, nullable=False)
    search_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"SearchTerms('{self.search_term}', '{self.search_date}')"


