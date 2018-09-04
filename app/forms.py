from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, IntegerField, PasswordField, BooleanField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from app.models import User


class RegistrationForm(FlaskForm):
    '''
    This is registraton form where we must type our nickname, name, surname
    '''
    nickname = StringField('Nickname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    position = RadioField('Position', validators=[DataRequired()], choices=[('B','build'), ('O','office')])
    password = PasswordField('Password', validators=[DataRequired(),])
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
            raise ValidationError('Please use a different username.')


class LoginForm(FlaskForm):
    """
    This is login form where we must type our nickname
    """
    nickname = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remeber_me = BooleanField('Remeber me')
    submit = SubmitField('Log in')


class EditProfileForm(FlaskForm):
    """
    Arguments:
        FlaskForm edit profile  -- type som thing about you, you can change you position, phone number, nickname
    """
    nickname = StringField('Nickname', validators=[DataRequired()])
    description = TextAreaField('About me', validators=[Length(min=0, max=200)])
    phone = IntegerField('Phone number', validators=[NumberRange(min=0, max=10)])
    position = RadioField('Position', validators=[DataRequired()], choices=[('B','build'), ('O','office')])
    submit = SubmitField('Submit')
