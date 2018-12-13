from wtforms import Form, StringField, validators, BooleanField, SelectMultipleField


class AddAdminForm(Form):
    emp_id = StringField('Employee ID', [validators.data_required()])
    name = StringField('Employee Name', )
    super_admin = BooleanField('Super Admin', default=False)
    roles = SelectMultipleField('Roles')
