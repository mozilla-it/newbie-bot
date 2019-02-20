from wtforms import Form, StringField, TextAreaField, validators, IntegerField, BooleanField, FieldList, SelectMultipleField, SelectField
from newb import location_choices, country_choices, employee_type_choices


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
    country = SelectMultipleField('Country', validators=[validators.data_required()], choices=country_choices)
    tagitems = StringField('Tags')
    location = SelectMultipleField('Office Location', validators=[validators.data_required()],
                           choices=location_choices)
    emp_type = SelectMultipleField('Employee Type', validators=[validators.data_required()],
