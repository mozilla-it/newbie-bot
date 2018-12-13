from wtforms import Form, StringField, TextAreaField


class SlackDirectMessage(Form):
    message_text = TextAreaField('Message Value')
    message_user = StringField('To User')

