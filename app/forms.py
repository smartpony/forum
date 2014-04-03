#
# Описание форм для ввода данных
#

from flask_wtf import Form
from wtforms import TextField, TextAreaField, FileField
from wtforms.validators import DataRequired

class RecepientForm(Form):
    recepient = TextField(validators=[DataRequired()])

class TopicForm(Form):
    topic = TextField(validators=[DataRequired()])

class MessageForm(Form):
    message = TextAreaField(validators=[DataRequired()])

class LoginForm(Form):
    login = TextField()
    password = TextField()

class RegisterForm(Form):
    login = TextField()
    email = TextField()
    password = TextField()
    password_confirm = TextField()

class ProfileForm(Form):
    city = TextField()
    country = TextField()
    email = TextField()
    avatar = FileField()

class SearchForm(Form):
    words = TextField(validators=[DataRequired()])