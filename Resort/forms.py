from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegisterForm(FlaskForm):
    name = StringField('User Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=11, max=11)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    rememberMe = BooleanField('Remember Me')
    submit = SubmitField('Login')
