from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, IntegerField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email


class Registration(FlaskForm):
    '''
    This is registraton form where we must type our nickname, name, surname, 
    '''
    nickname = StringField('Nickname', validators=['DataRequired'])
    name = StringField('Name', validators=['DataRequired'])
    surname = StringField('Surname', validators=['DataRequired'])
    position = RadioField('Position', validators=['DataRequired'], choices=[('value','build'), ('value_2','office')])
    email = StringField('Email', validators=['DataRequired','Email'])
    phone = IntegerField('Phone number', validators=['DataRequired'])


class Login(FlaskForm):
    """
    This is login form where we must type our nickname
    """
    nickname = StringField('Nickname', validators=['DataRequired'])
    nickname = PasswordField('Password', validators=['DataRequired'])
    remeber_me = BooleanField('Remeber me')
    submit = SubmitField('Log in')
