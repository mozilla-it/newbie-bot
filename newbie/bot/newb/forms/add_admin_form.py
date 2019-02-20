from wtforms import Form, StringField, validators, BooleanField, SelectMultipleField, SelectField
from newb import admin_team_choices

default_choices = []
class AddAdminForm(Form):
    emp_id = StringField('Employee ID', [validators.data_required()])
    name = StringField('Employee Name', )
    super_admin = BooleanField('Super Admin', default=False)
    roles = SelectMultipleField('Roles')
    team = SelectField('Team', validators=[validators.data_required()], choices=admin_team_choices)
