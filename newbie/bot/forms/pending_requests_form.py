from wtforms import Form, StringField, RadioField, HiddenField, validators, SelectField
from newbie.bot import admin_team_choices


class PendingRequestsForm(Form):
    decision = RadioField('Admin Decision', choices=[('approve', 'Approve'), ('deny', 'Deny')],
                          validators=[validators.data_required()])
    comment = StringField('Comment')
    person = HiddenField()
    team = SelectField('Team', validators=[validators.data_required()],
                       choices=admin_team_choices)
