#
# Описание форм для ввода данных
#

from flask_wtf import Form
from wtforms import TextField, TextAreaField, FileField
from wtforms.validators import DataRequired

class PostingForm(Form):
    topic = TextField(validators=[DataRequired()])
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