from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, IntegerField, PasswordField, BooleanField, SubmitField, PasswordField, TextAreaField, FileField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError, Length, NumberRange
import requests
from app.models import User, Company, Build, Employee, JobApp, Post


class RegistrationForm(FlaskForm):
    '''
    This is registraton form where we must type our nickname, name, surname
    '''
    nickname = StringField('Nickname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    gender = RadioField('Gender', validators=[DataRequired()], choices=[('male','Male'), ('female','Female')])
    password = PasswordField('Password', validators=[DataRequired(),Length(8,message='At least 8 characters.')])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    email = StringField('Email', validators=[DataRequired(),Email() ])
    phone = StringField('Phone number', validators=[DataRequired()])
    submit = SubmitField('Register in')

    def validate_nickname(self, nickname):
        user = User.query.filter_by(nickname=nickname.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email.')

    def validate_password(self, password):
        p = password.data
        n = 0
        u = 0
        l = 0
        for i in p:
            if i.islower():
                l += 1
            if i.isupper():
                u += 1
            if i.isdigit():
                n += 1
        if n == 0 or u == 0 or l == 0:
            raise ValidationError('Password must contain one digit, one lowercase letter one uppercase letter.')


class LoginForm(FlaskForm):
    """
    This is login form where we must type our nickname
    """
    nickname = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remeber_me = BooleanField('Remeber me')
    submit = SubmitField('Log in')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    submit = SubmitField('Passowrd Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(),])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password2')])
    submit = SubmitField('Request Password Reset')

    def validate_password(self, password):
        p = password.data
        n = 0
        u = 0
        l = 0
        for i in p:
            if i.islower():
                l += 1
            if i.isupper():
                u += 1
            if i.isdigit():
                n += 1
        if n == 0 or u == 0 or l == 0:
            raise ValidationError('Password must contain one digit, one lowercase letter one uppercase letter.')