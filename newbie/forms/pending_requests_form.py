from wtforms import Form, StringField, RadioField, HiddenField, validators


class PendingRequestsForm(Form):
    decision = RadioField('Admin Decision', choices=[('approve', 'Approve'), ('deny', 'Deny')],
                          validators=[validators.data_required()])
    comment = StringField('Comment')
    person = HiddenField()
