from wtforms import Form, StringField, TextAreaField, validators, IntegerField, BooleanField, FieldList, SelectMultipleField, SelectField



class AddMessageForm(Form):
    message_type = SelectField('Message Type', validators=[validators.data_required()], choices=[
        ('best_practices', 'Reminder: Best Practices'),
        ('deadline', 'Reminder: Deadline'),
        ('instruction', 'Instruction: How-to'),
        ('informational', 'Informational: Awareness')
    ])
    # category = SelectField('Category', validators=[validators.data_required()], choices=[
    #     ('Procedural', 'Prodedural'), ('Welcome', 'Welcome'), ('Failure', 'Failure / fallback'),
    #     ('Help', 'Help'), ('Rating', 'Rating request'), ('Opt-out', 'Opt-out'), ('Cultural', 'Cultural'),
    #     ('Orientation', 'Orientation')
    # ])
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
    # frequency = SelectField('Frequency', validators=[validators.data_required()], choices=[
    #     ('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')
    # ])
    send_date = StringField('Send Date')
    send_once = BooleanField('Specific Date', default=False)
    text = TextAreaField('Message Body')
    # number_of_sends = IntegerField(
    #     'Number of Sends',
    #     [validators.number_range(min=1, max=10, message='Must be between 1 and 10.'), validators.data_required()],
    #     default=1)
    country = SelectField('Country', validators=[validators.data_required()], choices=[('ALL', 'ALL'), ('US', 'US'),
                                                                                       ('CA', 'CA')])
    tagitems = StringField('Tags')
    location = SelectField('Office Location', validators=[validators.data_required()],
                           choices=[('mozilla', 'Mozilla Offices'), ('remotees', 'Remote Workers')])
    emp_type = SelectField('Employee Type', validators=[validators.data_required()],
                           choices=[('FTE', 'FTE'), ('contractor', 'Contractor'), ('intern', 'Intern')])
