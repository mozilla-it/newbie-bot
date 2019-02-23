import datetime

from newb import db

class SearchTerms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String(100), unique=False, nullable=False)
    search_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"SearchTerms('{self.search_term}', '{self.search_date}')"
