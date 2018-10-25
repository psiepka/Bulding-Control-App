from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, IntegerField, PasswordField, BooleanField, SubmitField, PasswordField, TextAreaField, FileField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError, Length, NumberRange
import requests
from app import app
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


class EditProfileForm(FlaskForm):
    """
    Arguments:
        FlaskForm edit profile  -- type som thing about you, you can change you position, phone number, nickname
    """
    nickname = StringField('Nickname', validators=[DataRequired()])
    avatar = FileField('Change avatar')
    description = TextAreaField('About me', validators=[Length(min=0, max=200)])
    phone = IntegerField('Phone number', validators=[DataRequired()])
    gender = RadioField('Gender', validators=[DataRequired()], choices=[('male','Male'), ('female','Female')])
    linkedin = StringField('Linkedin')
    curriculum_vitae = FileField('Curriculum Vitae')
    submit = SubmitField('Submit')

    def __init__(self, orginal_name, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.orginal_name = orginal_name

    def validate_nickname(self, nickname):
        if nickname.data != self.orginal_name:
            user = User.query.filter_by(nickname=nickname.data).first()
            if user is not None:
                raise ValidationError('Please use a different nickname.')

    def validate_avatar(self, avatar):
        if avatar.data:
            file_ext = avatar.data.filename.rsplit('.',1)[1].lower()
            if file_ext not in app.config['IMAGES']:
                raise ValidationError('File with this extension is unacceptable.')

    def validate_linkedin(self, linkedin):
        if linkedin.data:
            if not linkedin.data.startswith('https://www.linkedin.com/'):
                raise ValidationError('Please type correct adress to your linkedin profile.')

    def validate_curriculum_vitae(self, curriculum_vitae):
        if curriculum_vitae.data:
            file_ext = curriculum_vitae.data.filename.rsplit('.',1)[1].lower()
            if file_ext not in app.config['ALLOWED_EXTENSIONS']:
                raise ValidationError('File with this extension is unacceptable.')


class CompanyForm(FlaskForm):
    """
    company adding form
    """
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Company description', validators=[Length(min=0, max=1000)])
    web_page = StringField('Web page *')
    submit = SubmitField('Submit')

    def validate_name(self, name):
        name = Company.query.filter_by(name=name.data).first()
        if name is not None:
            raise ValidationError('Please use a different name of your Company.')

    def validate_web_page(self, web_page):
        if web_page.data:
            web = Company.query.filter_by(web_page=web_page.data).first()
            if web is not None:
                raise ValidationError('For this web page company already exist.')
            try:
                r = requests.get(web_page.data)
                if r.status_code is not 200:
                    raise ValidationError("This page doesn`t work.")
            except requests.exceptions.ConnectionError:
                raise ValidationError("This page dosn`t exist.")


class EditCompanyForm(FlaskForm):
    """
    company adding form
    """
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Company description', validators=[Length(min=0, max=1000)])
    web_page = StringField('Web page *')
    submit = SubmitField('Submit')

    def __init__(self, orginal_name, *args, **kwargs):
        super(EditCompanyForm, self).__init__(*args, **kwargs)
        self.orginal_name = orginal_name

    def validate_name(self, name):
        if name.data != self.orginal_name:
            name = Company.query.filter_by(name=name.data).first()
            if name is not None:
                raise ValidationError('Please use a different name of your Company.')

    def validate_web_page(self, web_page):
        if web_page.data:
            web = Company.query.filter_by(web_page=web_page.data).first()
            if web is not None:
                raise ValidationError('For this web page company already exist.')
            try:
                r = requests.get(web_page.data)
                if r.status_code is not 200:
                    raise ValidationError("This page doesn`t work.")
            except requests.exceptions.ConnectionError:
                raise ValidationError("This page dosn`t exist.")


class BuildForm(FlaskForm):
    """
    Build addding form
    Arguments:
    name - String, specification String, worth Integer, place String(place on map), start_date, end_date, creator_id, contractor_id
    """
    name = StringField('Name', validators=[DataRequired()])
    specification = StringField('Specification', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    worth = IntegerField('Value', validators=[DataRequired()])
    place = StringField('Place', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_name(self, name):
        name = Build.query.filter_by(name=name.data).first()
        if name is not None:
            raise ValidationError('Please use a different name of Building.')


class PostForm(FlaskForm):
    """
    Post adding form
    """
    body = TextAreaField('Post', validators=[DataRequired(), Length(1,2000)])
    submit = SubmitField('Submit')


class JobAppForm(FlaskForm):
    salary = IntegerField('Salary', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditBuildForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    specification = StringField('Specification', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    start_date = DateField('Start date', validators=[Optional()])
    end_date = DateField('End date',  validators=[Optional()])
    contractor = StringField('Company')
    worth = IntegerField('Value', validators=[DataRequired()])
    place = StringField('Place', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, orginal_name, *args, **kwargs):
        super(EditBuildForm, self).__init__(*args, **kwargs)
        self.orginal_name = orginal_name

    def validate_name(self, name):
        if name.data != self.orginal_name:
            name = Build.query.filter_by(name=name.data).first()
            if name is not None:
                raise ValidationError('Please use a different name of Building.')

    def validate_contractor(self, contractor):
        if contractor.data:
            company = Company.query.filter_by(name=contractor.data).first()
            if company is None:
                raise ValidationError('This company doesnt exist in app')


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