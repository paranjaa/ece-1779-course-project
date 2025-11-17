from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import validators
from wtforms.fields.simple import PasswordField

from utils import roles

class EmptyForm(FlaskForm):
    pass


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.InputRequired()])
    password = PasswordField('Password', validators=[validators.InputRequired()])
    submit = SubmitField('Log In')


class EnrollmentForm(FlaskForm):
    username = StringField("username", validators=[validators.InputRequired()])
    password = PasswordField("password", validators=[validators.InputRequired()])
    role = SelectField("Choose a role", choices=[
        (roles.MANAGER.value, "Manager"),
        (roles.USER.value, "User"),
    ])