import datetime
from newbie import db


class AuthGroups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groups = db.Column(db.String(150), unique=True, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"AuthGroups('{self.groups}', {self.created_date}')"
