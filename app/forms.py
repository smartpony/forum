#
# Описание форм для ввода данных
#

from flask_wtf import Form
from wtforms import TextField, TextAreaField


class PostingForm(Form):
    topic = TextField()
    message = TextAreaField()

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
    avatar = TextField()