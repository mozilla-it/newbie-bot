from wtforms import Form, SelectMultipleField

class AddAdminRequest(Form):
    roles = SelectMultipleField('Roles')
