from wtforms import Form, StringField, TextAreaField, validators, IntegerField, BooleanField



class AddMessageForm(Form):
    message_type = StringField('Message Type', [validators.data_required()])
    category = StringField('Category', [validators.data_required()])
    title = StringField('Title', [validators.data_required()])
    title_link = StringField('Title Link')
    send_day = IntegerField(
        'Send Day',
        [validators.number_range(min=1, max=31, message='Must be valid day.')],
        default=1)
    send_time = IntegerField(
        'Send Hour',
        [validators.number_range(min=0, max=23, message='Must be valid hour (0 - 23).')],
        default=9)
    frequency = StringField('Frequency')
    send_date = StringField('Send Date')
    send_once = BooleanField('Specific Date', default=False)
    text = TextAreaField('Message Value')
    number_of_sends = IntegerField(
        'Number of Sends',
        [validators.number_range(min=1, max=10, message='Must be between 1 and 10.'), validators.data_required()],
        default=1)
    country = StringField('Country', [validators.data_required()])


