from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, IntegerField, PasswordField, BooleanField, SubmitField, PasswordField, TextAreaField, FileField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError, Length, NumberRange
import requests
from app.models import User, Company, Build, Employee, JobApp, Post


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
