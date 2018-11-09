from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, IntegerField, PasswordField, BooleanField, SubmitField, PasswordField, TextAreaField, FileField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError, Length, NumberRange
import requests
from app.models import User, Company, Build, Employee, JobApp, Post


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


class JobAppForm(FlaskForm):
    salary = IntegerField('Salary', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    submit = SubmitField('Submit')

