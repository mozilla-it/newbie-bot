from wtforms import Form, StringField, validators, IntegerField


class AddEmployeeForm(Form):
    first_name = StringField('First Name', [validators.length(min=2, max=50)])
    last_name = StringField('Last Name', [validators.length(min=3, max=50)])
    email = StringField('Email', [validators.email(message="not a valid email")])
    city = StringField('City', [validators.length(min=2, max=50)])
    state = StringField('State', [validators.length(min=2, max=2)])
    country = StringField('Country', [validators.length(min=2, max=2)])
    timezone = StringField('Timezone')
    emp_id = IntegerField('Employee Id')
    slack_handle = StringField('Slack Handle', [validators.length(min=4, max=25)])
    start_date = StringField('Start Date')
    phone = StringField('Phone', [validators.length(min=10, max=15)])
    manager_id = IntegerField('Manager ID')
    title = StringField('Title', [validators.length(min=3, max=50)])
    picture = StringField('Picture URL')