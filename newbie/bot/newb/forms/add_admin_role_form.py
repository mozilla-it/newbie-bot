from wtforms import Form, StringField, validators


class AddAdminRoleForm(Form):
    role_name = StringField('Role Name', [validators.length(min=2, max=50)])
    role_description = StringField('Role Description', [validators.length(min=3, max=100)])
