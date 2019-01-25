from wtforms import Form, StringField, validators, \
    SelectMultipleField, SelectField, \
    TextAreaField, IntegerField, BooleanField, RadioField, HiddenField
from .config import admin_team_choices, location_choices, country_choices, employee_type_choices

default_choices = []


class AddAdminForm(Form):
    emp_id = StringField('Employee ID', [validators.data_required()])
    name = StringField('Employee Name', )
    super_admin = BooleanField('Super Admin', default=False)
    roles = SelectMultipleField('Roles')
    team = SelectField('Team', validators=[validators.data_required()],
                       choices=admin_team_choices)


class AddAdminRequest(Form):
    roles = SelectMultipleField('Roles')


class AddAdminRoleForm(Form):
    role_name = StringField('Role Name', [validators.length(min=2, max=50)])
    role_description = StringField('Role Description', [validators.length(min=3, max=100)])


class AddEmployeeForm(Form):
    first_name = StringField('First Name', [validators.length(min=2, max=50)])
    last_name = StringField('Last Name', [validators.length(min=3, max=50)])
    email = StringField('Email', [validators.email(message="not a valid email")])
    country = StringField('Country', [validators.length(min=2, max=2)])
    timezone = StringField('Timezone')
    emp_id = StringField('Employee Id')
    slack_handle = StringField('Slack Handle', [validators.length(min=4, max=25)])
    start_date = StringField('Start Date')
    manager_id = StringField('Manager ID')


class AddMessageForm(Form):
    message_type = SelectField('Message Type', validators=[validators.data_required()], choices=[
        ('best_practices', 'Reminder: Best Practices'),
        ('deadline', 'Reminder: Deadline'),
        ('instruction', 'Instruction: How-to'),
        ('informational', 'Informational: Awareness')
    ])
    topic = StringField('Topic', [validators.data_required()])
    linkitems = StringField('Title Link')
    send_day = IntegerField(
        'Send Day',
        [validators.number_range(min=1, max=31, message='Must be valid day.')],
        default=1)
    send_time = IntegerField(
        'Send Hour',
        [validators.number_range(min=0, max=23, message='Must be valid hour (0 - 23).')],
        default=9)
    send_date = StringField('Send Date')
    send_once = BooleanField('Specific Date', default=False)
    text = TextAreaField('Message Body')
    country = SelectField('Country', validators=[validators.data_required()], choices=country_choices)
    tagitems = StringField('Tags')
    location = SelectField('Office Location', validators=[validators.data_required()],
                           choices=location_choices)
    emp_type = SelectField('Employee Type', validators=[validators.data_required()],
                           choices=employee_type_choices)


class PendingRequestsForm(Form):
    decision = RadioField('Admin Decision', choices=[('approve', 'Approve'), ('deny', 'Deny')],
                          validators=[validators.data_required()])
    comment = StringField('Comment')
    person = HiddenField()
    team = SelectField('Team', validators=[validators.data_required()],
                       choices=admin_team_choices)


class SlackDirectMessage(Form):
    message_text = TextAreaField('Message Value')
    message_user = StringField('To User')
