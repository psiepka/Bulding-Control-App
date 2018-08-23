from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, IntegerField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email


class RegistrationForm(FlaskForm):
    '''
    This is registraton form where we must type our nickname, name, surname, 
    '''
    nickname = StringField('Nickname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    position = RadioField('Position', validators=[DataRequired()], choices=[('B','build'), ('O','office')])
    email = StringField('Email', validators=[DataRequired(),'Email'])
    phone = IntegerField('Phone number', validators=[DataRequired()])
    submit = SubmitField('Register in')


class LoginForm(FlaskForm):
    """
    This is login form where we must type our nickname
    """
    nickname = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remeber_me = BooleanField('Remeber me')
    submit = SubmitField('Log in')
