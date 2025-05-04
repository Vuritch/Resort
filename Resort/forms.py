from flask_wtf import FlaskForm
from wtforms import  FloatField, IntegerField, SelectField, StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Email, EqualTo, Length, DataRequired, Regexp,Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired, MultipleFileField

from app import ALLOWED_EXTENSIONS
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message="Name must be between 2 and 50 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address"),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long"),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', 
               message="Password must contain at least one letter and one number")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    # New admin forms
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('guest','Guest'),('admin','Admin')], validators=[DataRequired()])
    submit = SubmitField('Save')

class RoomTypeForm(FlaskForm):
    name           = StringField('Name', validators=[DataRequired(), Length(max=50)])
    description    = TextAreaField('Description', validators=[Optional()])
    base_price     = FloatField('Base Price', validators=[DataRequired(), NumberRange(min=0)])
    max_guests     = IntegerField('Max Guests', validators=[DataRequired(), NumberRange(min=1)])
    # ←— file‐upload fields:
    main_image     = FileField(
        'Main Image',
        validators=[
            FileRequired(),
            FileAllowed(ALLOWED_EXTENSIONS, 'Only images!')
        ]
    )
    gallery_images = MultipleFileField(
        'Gallery Images',
        validators=[FileAllowed(ALLOWED_EXTENSIONS, 'Only images!')]
    )
    features       = StringField('Features (comma-separated)', validators=[Optional()])
    is_luxury      = BooleanField('Luxury?')
    luxury_label   = StringField('Luxury Label', validators=[Optional(), Length(max=50)])
    submit         = SubmitField('Save')

class ExtraServiceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    type = SelectField('Type', choices=[('dining','Dining'),('service','Service'),('bed','Bed')], validators=[DataRequired()])
    submit = SubmitField('Save')

class GuestOptionForm(FlaskForm):
    adult_count = IntegerField('Number of Adults', validators=[DataRequired(), NumberRange(min=1)])
    child_count = IntegerField('Number of Children', validators=[DataRequired(), NumberRange(min=0)])
    label = StringField('Label', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Save')
