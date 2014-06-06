#
# Описание форм для ввода данных
#

from flask_wtf import Form
from wtforms import TextField, TextAreaField, FileField
from wtforms_html5 import IntegerField
from wtforms.validators import DataRequired, EqualTo

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
    login = TextField(validators=[DataRequired()])
    email = TextField(validators=[DataRequired()])
    password = TextField(validators=[DataRequired()])
    password_confirm = TextField(validators=[DataRequired(), EqualTo('password')])

class ProfileForm(Form):
    city = TextField()
    country = TextField()
    email = TextField()
    avatar_from_hdd = FileField()
    avatar_from_inet = TextField()

class SearchForm(Form):
    words = TextField(validators=[DataRequired()])

class FillForm(Form):
    topics = IntegerField()
    messages = IntegerField()